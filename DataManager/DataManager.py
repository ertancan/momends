__author__ = 'goktan'
from models import Provider
import importlib
from DataEnrich.EnrichDataWorker import EnrichDataWorker
from ExternalProviders.BaseProviderWorker import BasePhotoProviderWorker,BaseStatusProviderWorker,BaseLocationProviderWorker
from Outputs.AnimationManager.AnimationManagerWorker import AnimationManagerWorker
from models import Momend, MomendScore
from models import RawData
from Outputs.AnimationManager.models import OutData
from social_auth.db.django_models import UserSocialAuth
from LogManagers.Log import Log
from DataManagerUtil import DataManagerUtil
from django.db.models import Q
from django.conf import settings

class DataManager:
    def __init__(self, user):
        self.user = user
        self.momend = None

    status = dict() #keep the latest status of raw data collection

    def get_last_status(self):
        return self.status

    def create_momend(self, name, since, until, duration, #TODO check if dates has timezone information = tzinfo
                      privacy=Momend.PRIVACY_CHOICES['Private'], inc_photo=True, inc_status=True, inc_checkin=True,
                      enrichment_method=None, theme=None, scenario=None):
        raw_data = self.collect_user_data(since, until, inc_photo, inc_status, inc_checkin)
        enriched_data = self.enrich_user_data(raw_data, enrichment_method)
        self.momend = Momend(owner=self.user, name=name, momend_start_date=since, momend_end_date=until, privacy=privacy)
        self.momend.save()
        animation_worker = AnimationManagerWorker(self.momend)
        generated_layer, duration = animation_worker.generate_output(enriched_data, duration, theme, scenario) #TODO save the duration, to Momend table?
        self._create_momend_thumbnail()
        self.momend.save()

        score = MomendScore(momend = self.momend, provider_score = self._calculate_provider_score())
        score.save()
        return self.momend.id

    def collect_user_data(self, since, until, inc_photo, inc_status, inc_checkin):
        _raw_data = []
        _collect_count = dict()
        for _provider in Provider.objects.all():
            if UserSocialAuth.objects.filter(provider=str(_provider).lower()).filter(user=self.user).count()>0:
                worker = self._instantiate_provider_worker(_provider)
                if inc_photo and issubclass(worker.__class__,BasePhotoProviderWorker):
                    _raw_data = _raw_data + worker.collect_photo(self.user, since, until)
                    if not _raw_data:
                        self.status[str(_provider)+'_photo'] = 'Error'
                    else:
                        _collect_count['photo'] = _collect_count.get('photo', 0) + len(_raw_data)
                        self.status[str(_provider)+'_photo'] = 'Success'
                if inc_status and issubclass(worker.__class__,BaseStatusProviderWorker):
                    _raw_data = _raw_data + worker.collect_status(self.user, since, until)
                    if not _raw_data:
                        self.status[str(_provider)+'_status'] = 'Error'
                    else:
                        _collect_count['status'] = _collect_count.get('status', 0) + len(_raw_data)
                        self.status[str(_provider)+'_status'] = 'Success'
                if inc_checkin and issubclass(worker.__class__,BaseLocationProviderWorker):
                    _raw_data = _raw_data + worker.collect_checkin(self.user, since, until)
                    if not _raw_data:
                        self.status[str(_provider)+'_checkin'] = 'Error'
                    else:
                        _collect_count['checkin'] = _collect_count.get('checkin', 0) + len(_raw_data)
                        self.status[str(_provider)+'_checkin'] = 'Success'
        #all incoming data shall be saved here instead of collection place
        Log.debug('status:'+str(self.status))
        Log.debug('Collected Objects:'+str(_collect_count))
        for _obj in _raw_data:
            _obj.save()

        return _raw_data

    def enrich_user_data(self, raw_data, method=None):
        if not method:
            method = 'date'
        enriched_data = EnrichDataWorker.enrich_user_raw_data(raw_data) #TODO use method parameter
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
                        'momend_'+str(self.momend.pk)+'_thumb.jpg')
                    break
        except Exception as error:
            Log.error("Couldn't create thumbnail!-->"+str(error))

    def _instantiate_provider_worker(self, provider):
        """
        Instantiates the worker objects, which collects data etc., for given provider
        :param provider: models.Provider object
        :return:
        """
        mod = importlib.import_module('ExternalProviders.'+provider.package_name+'.'+provider.worker_name,provider.worker_name)
        cl = getattr(mod,provider.worker_name)
        return cl()

    def _calculate_provider_score(self):
        main_layer = self.momend.animationlayer_set.all()[1]
        used_objects = OutData.objects.filter(owner_layer = main_layer).filter(Q(raw__isnull = False))
        _score = 0
        for _out_data in used_objects:
            _score += _out_data.raw.share_count*5
            _score += _out_data.raw.comment_count*2
            _score += _out_data.raw.like_count

        return _score

