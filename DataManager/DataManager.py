__author__ = 'goktan'
from models import Provider
import importlib
from DataEnrich.EnrichDataWorker import EnrichDataWorker
from ExternalProviders.BaseProviderWorker import BasePhotoProviderWorker,BaseStatusProviderWorker,BaseLocationProviderWorker
from Outputs.AnimationManager.AnimationManagerWorker import AnimationManagerWorker
from models import Momend

class DataManager:
    def __init__(self, user):
        self.user = user

    def create_momend(self, name, since, until, duration, #TODO check if dates has timezone information = tzinfo
                      privacy=Momend.PRIVACY_CHOICES['Private'], inc_photo=True, inc_status=True, inc_checkin=True,
                      enrichment_method=None, theme=None, scenario=None):
        raw_data = self.collect_user_data(since, until, inc_photo, inc_status, inc_checkin)
        enriched_data = self.enrich_user_data(raw_data, enrichment_method)
        momend = Momend(owner=self.user, name=name, momend_start_date=since, momend_end_date=until, privacy=privacy)
        momend.save()
        animation_worker = AnimationManagerWorker(momend)
        momend_animation = animation_worker.generate_output(enriched_data, duration, theme, scenario)
        return momend_animation

    def collect_user_data(self, since, until, inc_photo, inc_status, inc_checkin):
        _raw_data = []
        for obj in Provider.objects.all():
            if getattr(self.user, obj.module_name.lower()+'_set').count()>0:
                worker = self._instantiate_provider_worker(obj)
                if inc_photo and issubclass(worker.__class__,BasePhotoProviderWorker):
                    _raw_data = _raw_data + worker.collect_photo(self.user, since, until)
                if inc_status and issubclass(worker.__class__,BaseStatusProviderWorker):
                    _raw_data = _raw_data + worker.collect_status(self.user, since, until)
                if inc_checkin and issubclass(worker.__class__,BaseLocationProviderWorker):
                    _raw_data = _raw_data + worker.collect_checkin(self.user, since, until)
        #all incoming data shall be saved here instead of collection place
        for obj in _raw_data:
            obj.save()

        return _raw_data

    def enrich_user_data(self, raw_data, method=None):
        if not method:
            method = 'date'

        enrich_worker = EnrichDataWorker(self.user)
        enriched_data = enrich_worker.enrich_data(raw_data) #TODO use method parameter
        return enriched_data


    def _instantiate_provider_worker(self, provider):
        mod = importlib.import_module('ExternalProviders.'+provider.package_name+'.'+provider.worker_name,provider.worker_name)
        cl = getattr(mod,provider.worker_name)
        return cl()

