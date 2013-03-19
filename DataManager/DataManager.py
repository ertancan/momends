from django.db import IntegrityError

__author__ = 'goktan'
from models import Provider
from DataEnrich.DataEnrichManager import DataEnrichManager
from ExternalProviders.BaseProviderWorker import BasePhotoProviderWorker, BaseStatusProviderWorker, BaseLocationProviderWorker
from models import encode_id
from models import Momend, MomendStatus
from models import RawData
from models import DataEnrichmentScenario
from Outputs.AnimationManager.models import OutData
from social_auth.db.django_models import UserSocialAuth
from LogManagers.Log import Log
from DataManagerUtil import DataManagerUtil
from django.db.models import Q
from django.conf import settings
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
            if kwargs['is_date']:
                try:
                    self.momend.momend_start_date = kwargs['since']
                    self.momend.momend_end_date = kwargs['until']
                except KeyError:
                    self._handle_momend_create_error('Parameter error. Please try again')
            else:
                self.status = 'Not supported yet!'
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
        _user_name = self.user.first_name.lower()
        if Momend.objects.filter(owner=self.user).count() == 0:
            return _user_name + "'s first momend"

        _momend_name = _user_name + "'s"

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
        if _friends:
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
        _raw_data = []
        _collect_count = dict()
        _collect_status = dict()
        for _provider in Provider.objects.all():
            if UserSocialAuth.objects.filter(provider=str(_provider)).filter(user=self.user).count() > 0:
                worker = _provider.instantiate_provider_worker()
                if inc_photo and issubclass(worker.__class__, BasePhotoProviderWorker):
                    _collected = worker.collect_photo(self.user, **kwargs)
                    if not _collected:
                        _collect_status[str(_provider)+'_photo'] = 'Error'
                    else:
                        _raw_data += _collected
                        _collect_count['photo'] = _collect_count.get('photo', 0) + len(_raw_data)
                        _collect_status[str(_provider)+'_photo'] = 'Success'
                if inc_status and issubclass(worker.__class__, BaseStatusProviderWorker):
                    _collected = worker.collect_status(self.user, **kwargs)
                    if not _collected:
                        _collect_status[str(_provider)+'_status'] = 'Error'
                    else:
                        _raw_data += _collected
                        _collect_count['status'] = _collect_count.get('status', 0) + len(_raw_data)
                        _collect_status[str(_provider)+'_status'] = 'Success'
                if inc_checkin and issubclass(worker.__class__, BaseLocationProviderWorker):
                    _collected = worker.collect_checkin(self.user, **kwargs)
                    if not _collected:
                        _collect_status[str(_provider)+'_checkin'] = 'Error'
                    else:
                        _raw_data += _collected
                        _collect_count['checkin'] = _collect_count.get('checkin', 0) + len(_raw_data)
                        _collect_status[str(_provider)+'_checkin'] = 'Success'
        #all incoming data shall be saved here instead of collection place
        Log.debug('status:'+str(_collect_status))
        Log.debug('Collected Objects:'+str(_collect_count))
        for _obj in _raw_data:
            try:
                _obj.save()
            except IntegrityError as e:
                Log.debug('Raw data save error:'+str(e))

        return _raw_data, _collect_status

    def enrich_user_data(self, raw_data, raw_data_filter=None, method=None):
        """
        Enrich collected raw data according to the parameters.
        @param raw_data_filter: filters to be applied to the collected data, (Dictionary):
            Currently only supports 'friends' filter, an array of friend ids, in format 'providername-id', should be mapped to key 'friends'
        """
        if not method:
            method = 'date'

        _enrich_scenario = DataEnrichmentScenario.objects.order_by('pk').reverse()[0]  # TODO: Using the latest enrichment scenario, use the scenario from parameter instaed
        _enrich_manager = DataEnrichManager(self.user, raw_data, _enrich_scenario)
        if raw_data_filter:
            _enrich_manager.filter_user_data(raw_data_filter)
        _enriched_data = _enrich_manager.get_enriched_user_raw_data()
        return _enriched_data

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
                    self.momend.thumbnail = DataManagerUtil.create_photo_thumbnail(settings.SAVE_PREFIX + data.final_data_path,
                                                                                   'momend_' + str(self.momend.pk) + '_thumb.jpg')
                    break
        except Exception as error:
            Log.error("Couldn't create thumbnail!-->"+str(error))

    def _calculate_provider_score(self):
        main_layer = self.momend.animationlayer_set.all()[1]
        used_objects = OutData.objects.filter(owner_layer=main_layer).filter(Q(raw__isnull=False))
        _score = 0
        for _out_data in used_objects:
            _score += _out_data.raw.share_count*5
            _score += _out_data.raw.comment_count*2
            _score += _out_data.raw.like_count

        return _score

    def _handle_momend_create_error(self, user_message, log_message=None):
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
