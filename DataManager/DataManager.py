from django.db import IntegrityError

__author__ = 'goktan'
from models import Provider
import importlib
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

    def create_momend(self, name, duration, mail,
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

            self.momend = Momend(owner=self.user, name=name, privacy=privacy)
            if kwargs['is_date']:
                try:
                    self.momend.momend_start_date = kwargs['since']
                    self.momend.momend_end_date = kwargs['until']
                except KeyError:
                    self.status = 'Missing parameters for date option'
                    return None
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
            tasks.create_momend_task.delay(self.user.id, self.momend.id, duration, mail, theme,
                                           scenario, inc_photo, inc_status, inc_checkin, enrichment_method, **kwargs)
            return _cryptic_id
        except Exception as e:
            self._handle_momend_create_error('Error while creating the momend. Please try again!', 'Exception: '+str(e)[:255])
            Log.error(traceback.format_exc())

        return True

    def collect_user_data(self, inc_photo, inc_status, inc_checkin, **kwargs):  # TODO concatenation fail if cannot connect to facebook or twitter (fixed on status)
        _raw_data = []
        _collect_count = dict()
        _collect_status = dict()
        for _provider in Provider.objects.all():
            if UserSocialAuth.objects.filter(provider=str(_provider).lower()).filter(user=self.user).count() > 0:
                worker = self._instantiate_provider_worker(_provider)
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

    def enrich_user_data(self, raw_data, method=None):
        if not method:
            method = 'date'
        _enrich_scenario = DataEnrichmentScenario.objects.order_by('pk').reverse()[0]  # TODO: Using the latest enrichment scenario, use the scenario from parameter instaed
        _enrich_manager = DataEnrichManager(self.user, raw_data, _enrich_scenario)
        enriched_data = _enrich_manager.get_enriched_user_raw_data()
        return enriched_data

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

    def _instantiate_provider_worker(self, provider):
        """
        Instantiates the worker objects, which collects data etc., for given provider
        :param provider: models.Provider object
        :return:
        """
        mod = importlib.import_module('ExternalProviders.' + provider.package_name + '.' + provider.worker_name, provider.worker_name)
        cl = getattr(mod, provider.worker_name)
        return cl()

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
        self.status = user_message
        self.momend_status.message = user_message
        self.momend_status.status = MomendStatus.MOMEND_STATUS['Error']
        self.momend_status.save()
