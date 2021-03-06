from django.db import IntegrityError

__author__ = 'goktan'
from models import Provider
from DataEnrich.DataEnrichManager import DataEnrichManager
from DataEnrich.DataEnrichManager import TemporaryEnrichedObjectHolder
from ExternalProviders.BaseProviderWorker import BasePhotoProviderWorker, BaseStatusProviderWorker, BaseLocationProviderWorker
from models import encode_id
from models import Momend, MomendStatus
from models import RawData
from models import DataEnrichmentScenario
from Outputs.AnimationManager.models import OutData
from social_auth.db.django_models import UserSocialAuth
from LogManagers.Log import Log
from DataManagerUtil import DataManagerUtil
from DataManagerUtil import CloudFile
from django.db.models import Q
import traceback
import tasks
import datetime
import pytz


class DataManager:
    def __init__(self, user, momend=None, momend_status=None):
        self.user = user
        self.momend = momend
        self.momend_status = momend_status

    status = ''  # keep the latest status of raw data collection

    def get_last_status(self):
        return self.status

    def create_momend(self, duration, send_mail, name=None,
                      privacy=Momend.PRIVACY_CHOICES['Private'], inc_photo=True, inc_status=True, inc_checkin=True,
                      enrichment_method=None, theme=None, scenario=None, **kwargs):
        """
        Initiates the momend create process.
        Checks if it there is any reasons not to create a momends (e.g. creating another momend, problems in parameters)
        And adds an async task to be processed by celery workers
        @param duration: approximate! duration of the momend (in seconds)
        @param send_mail: False; do not send mail to the owner after create
        @param name: name of the momend. uses directly if given, creates one if not
        @param inc_photo: Whether we should use photos while creating the momend or not
        @param inc_status: Whether we should use statuses while creating the momend or not
        @param inc_checkin: Whether we should use checkins or while creating the momend not
        @param enrichment_method what kind of enrichment should be used on user data. Decides automatically if None  TODO: don't enrich if None
        @param theme: Theme to be used on the momend, None for random
        @param scenario: Should be given if any specific scenario should be used
        Any additional settings could be given on kwargs (e.g. filters, is_date option etc.)
        """

        try:
            _time_limit = datetime.datetime.now().replace(tzinfo=pytz.UTC) - datetime.timedelta(minutes=5)
            if MomendStatus.objects.filter(owner=self.user)\
               .filter(~Q(status=MomendStatus.MOMEND_STATUS['Success']) & ~Q(status=MomendStatus.MOMEND_STATUS['Error']))\
               .filter(last_update__gt=_time_limit)\
               .exists():
                self.status = 'You are creating another momend right now. Please wait until it is ready.'
                return False

            if not name:
                name = self.generate_momend_name(theme, scenario, **kwargs)

            self.momend = Momend(owner=self.user, name=name, privacy=privacy)
            if kwargs['is_date']:  # Collect data by date, all providers but explictly excluded ones.
                try:
                    self.momend.momend_start_date = kwargs['since']
                    self.momend.momend_end_date = kwargs['until']
                except KeyError:
                    self._handle_momend_create_error('Parameter error. Please try again')
            elif kwargs['selected']:  # Create momend with selected raw data. Expects dictionary in this format;
                                                               # selected: {'provider-1':[data1, data2], 'provider-2':[data1, ...]}
                _now = datetime.datetime.now()
                _now = _now.replace(tzinfo=pytz.UTC)
                self.momend.momend_start_date = _now
                self.momend.momend_end_date = _now
            else:
                self._handle_momend_create_error('Create method not supported')
                return False
            self.momend.save()
            _cryptic_id = encode_id(self.momend.id)
            self.momend.cryptic_id = _cryptic_id
            self.momend.save()  # To save cryptic_id, doing this on pre_save not working since momend id is not ready, post_save also needs to update the momend
            self.momend_status = MomendStatus(momend=self.momend, owner=self.user)
            self.momend_status.status = MomendStatus.MOMEND_STATUS['Starting']
            self.momend_status.save()

            #Spawn a new task to create the momend
            tasks.create_momend_task.delay(self.user.id, self.momend.id, duration, send_mail, theme,
                                           scenario, inc_photo, inc_status, inc_checkin, enrichment_method, **kwargs)
            return _cryptic_id
        except Exception as e:
            self._handle_momend_create_error('Error while creating the momend. Please try again!', 'Exception: '+str(e)[:255])

        return True

    def generate_momend_name(self, theme, scenario, **kwargs):
        """
        Generates a name for the momend according to the parameters
        names it user's first momend if it is
        if the momend create mode is is_date then names according to day count
        """
        _user_name = self.user.first_name.lower()
        print _user_name
        if _user_name == '':
            _user_name = self.user.username
        if Momend.objects.filter(owner=self.user).count() == 0:
            return _user_name + "'s first momend"

        _momend_name = _user_name + "'s"

        if kwargs['selected']:
            return _momend_name + ' momend'
        if kwargs['is_date']:
            try:
                _name_date_part = ''
                _start_date = kwargs['since']
                _end_date = kwargs['until']
                if _end_date.date() == datetime.datetime.now().date():  # Momend ends today
                    _name_date_part += ' last'
                _delta = _end_date - _start_date
                _days = _delta.days
                Log.debug('Momend for ' + str(_days) + ' days')
                if _days >= 370:
                    _name_date_part += ' years'
                elif 360 < _days < 370:
                    _name_date_part += ' year'
                elif _days > 260:
                    _name_date_part += ' 9 months'
                elif _days > 170:
                    _name_date_part += ' 6 months'
                elif _days > 90:
                    _name_date_part += ' 3 months'
                elif _days > 32:
                    _name_date_part += ' months'
                elif _days > 25:
                    _name_date_part += ' month'
                elif _days > 7:
                    _name_date_part += ' weeks'
                elif _days == 7:
                    _name_date_part += ' week'
                if len(_name_date_part) > 0:
                    _momend_name += _name_date_part
                else:
                    _momend_name += ' momend'
            except KeyError:
                return _momend_name

        _friends = kwargs.get('friends', None)
        if _friends and len(_friends) > 0:
            if len(_friends) > 1:
                _momend_name += ' with friends'
            else:
                try:
                    _provider, _user_id = _friends[0].split('-')
                    _worker = Provider.objects.get(name=_provider).instantiate_provider_worker()
                    _friend_name = _worker.get_friend_name_from_id(self.user, _user_id)
                    _momend_name += ' with ' + _friend_name
                except:
                    self._handle_momend_create_error('An error occured, please refresh the page and try again', 'Error on generate momend name with friend')

        return _momend_name

    def collect_user_data(self, inc_photo, inc_status, inc_checkin, **kwargs):  # TODO concatenation fail if cannot connect to facebook or twitter (fixed on status)
        """
            Collects the user data from authenticated providers.
            ;param inc_* : whether or not to collect this type of data
            ;param provider_name-active : if these kinds of keys are given in kwargs and has value "False" this method won't collect data from them
            ;return RawData array
        """
        _raw_data = []
        _collect_count = dict()
        _collect_status = dict()
        if kwargs['is_date']:
            for _provider in Provider.objects.all():
                if UserSocialAuth.objects.filter(provider=_provider.name).filter(user=self.user).exists():
                    _provider_argument = _provider.name + '-active'
                    if _provider_argument in kwargs and (not kwargs[_provider_argument] or kwargs[_provider_argument].lower() == 'false'):  # Do not use this provider if parameters explicity say so
                        Log.info('Not collecting data from: ' + _provider.name)
                        continue

                    _worker = _provider.instantiate_provider_worker()
                    if inc_photo and issubclass(_worker.__class__, BasePhotoProviderWorker):
                        _collected = _worker.collect_photo(self.user, **kwargs)
                        if not _collected:
                            _collect_status[_provider.name + '_photo'] = 'Error'
                        else:
                            _raw_data += _collected
                            _collect_count['photo'] = _collect_count.get('photo', 0) + len(_collected)
                            _collect_status[_provider.name + '_photo'] = 'Success'
                    if inc_status and issubclass(_worker.__class__, BaseStatusProviderWorker):
                        _collected = _worker.collect_status(self.user, **kwargs)
                        if not _collected:
                            _collect_status[_provider.name + '_status'] = 'Error'
                        else:
                            _raw_data += _collected
                            _collect_count['status'] = _collect_count.get('status', 0) + len(_collected)
                            _collect_status[_provider.name + '_status'] = 'Success'
                    if inc_checkin and issubclass(_worker.__class__, BaseLocationProviderWorker):
                        _collected = _worker.collect_checkin(self.user, **kwargs)
                        if not _collected:
                            _collect_status[_provider.name + '_checkin'] = 'Error'
                        else:
                            _raw_data += _collected
                            _collect_count['checkin'] = _collect_count.get('checkin', 0) + len(_collected)
                            _collect_status[_provider.name + '_checkin'] = 'Success'

        elif kwargs['selected']:
            for i in range(len(RawData.DATA_TYPE)):
                _raw_data.append([])
            for _provider in kwargs['selected']:
                _worker = Provider.objects.get(name=_provider).instantiate_provider_worker()
                _selected_for_provider = kwargs['selected'][_provider]
                if 'photo' in _selected_for_provider and _selected_for_provider['photo'] and issubclass(_worker.__class__, BasePhotoProviderWorker):
                        _collected = _worker.collect_photo(self.user, selected=_selected_for_provider['photo'])
                        if not _collected:
                            _collect_status[_provider.name + '_photo'] = 'Error'
                        else:
                            _raw_data[RawData.DATA_TYPE['Photo']] += _collected
                            _collect_count['photo'] = _collect_count.get('photo', 0) + len(_collected)
                            _collect_status[_provider + '_photo'] = 'Success'
                if 'status' in _selected_for_provider and _selected_for_provider['status'] and issubclass(_worker.__class__, BaseStatusProviderWorker):
                    _collected = _worker.collect_status(self.user, selected=_selected_for_provider['status'])
                    if not _collected:
                        _collect_status[_provider + '_status'] = 'Error'
                    else:
                        _raw_data[RawData.DATA_TYPE['Status']] += _collected
                        _collect_count['status'] = _collect_count.get('status', 0) + len(_collected)
                        _collect_status[_provider + '_status'] = 'Success'
                if 'checkin' in _selected_for_provider and _selected_for_provider['checkin'] and issubclass(_worker.__class__, BaseLocationProviderWorker):
                    _collected = _worker.collect_checkin(self.user, selected=_selected_for_provider['checkin'])
                    if not _collected:
                        _collect_status[_provider + '_checkin'] = 'Error'
                    else:
                        _raw_data[RawData.DATA_TYPE['Checkin']] += _collected
                        _collect_count['checkin'] = _collect_count.get('checkin', 0) + len(_collected)
                        _collect_status[_provider + '_checkin'] = 'Success'

        #all incoming data shall be saved here instead of collection place
        Log.debug('status:'+str(_collect_status))
        Log.debug('Collected Objects:'+str(_collect_count))

        return _raw_data, _collect_status

    def enrich_user_data(self, raw_data, raw_data_filter=None, method=None):
        """
        Enrich collected raw data according to the parameters.
        @param raw_data_filter: filters to be applied to the collected data, (Dictionary):
            'friends' filter, an array of friend ids, in format 'providername-id', should be mapped to key 'friends'
            'chronological', boolean, preserves chronological order of collected data
        """
        if not method:
            method = 'date'

        _enrich_scenario = DataEnrichmentScenario.objects.order_by('pk').reverse()[0]  # TODO: Using the latest enrichment scenario, use the scenario from parameter instaed
        _enrich_manager = DataEnrichManager(self.user, raw_data, _enrich_scenario)
        if raw_data_filter:
            _enrich_manager.filter_user_data(raw_data_filter)
        _enriched_data = _enrich_manager.get_enriched_user_raw_data()
        if raw_data_filter['chronological']:  # TODO: TEST!
            _enriched_data = sorted(_enriched_data, key=lambda enriched: enriched.raw.create_date)
        return _enriched_data

    """
    Encapsulates the given RawData array. Places RawData objects into temporary wrapper (TemporaryEnrichedObjectHolder)
    @param raw_data: 2D array of RawData
    @return 2D array of TemporaryEnrichedObjectHolder
    """
    def encapsulate_raw_data(self, raw_data):
        _encapsualted = []
        for i in range(len(RawData.DATA_TYPE)):
                _encapsualted.append([])
                for _raw in raw_data[i]:
                    _encapsualted[i].append(TemporaryEnrichedObjectHolder(_raw, finalize=True))
        return _encapsualted

    def _create_momend_thumbnail(self):
        """
        Currently get a random used user photo of the momend and creates a thumbnail of its enhanced version
        :param momend: models.Momend object
        :return: same momend object with thumbnail field filled
        """
        try:
            out_data = self.momend.animationlayer_set.all()[1].outdata_set.order_by('?')
            for data in out_data:
                if data.raw and data.raw.type == RawData.DATA_TYPE['Photo']:
                    _cloud_file = CloudFile(data.raw)
                    self.momend.thumbnail = DataManagerUtil.create_photo_thumbnail(_cloud_file, 'momend_' + str(self.momend.pk) + '_thumb.jpg')
                    break
        except Exception as error:
            Log.error("Couldn't create thumbnail!-->"+str(error))

    def _calculate_provider_score(self):
        """
        Calculates a score for the momends according to the like, share and comment counts of the used data
        TODO: requires a better scoring algorithm
        """
        main_layer = self.momend.animationlayer_set.all()[1]
        used_objects = OutData.objects.filter(owner_layer=main_layer).filter(Q(raw__isnull=False))
        _score = 0
        for _out_data in used_objects:
            _score += _out_data.raw.share_count*5
            _score += _out_data.raw.comment_count*2
            _score += _out_data.raw.like_count

        return _score

    def _handle_momend_create_error(self, user_message, log_message=''):
        """
        Saves and logs the momend create process errors
        @param user_message: message that the user will see
        @param log_message: message to log/save to db
        """
        if log_message:
            Log.error(log_message)
        else:
            Log.error(user_message)
        _error_trace = traceback.format_exc()
        Log.error(_error_trace)
        self.status = user_message
        if self.momend_status:
            self.momend_status.log_message = log_message + _error_trace
            self.momend_status.message = user_message
            self.momend_status.status = MomendStatus.MOMEND_STATUS['Error']
            self.momend_status.save()
