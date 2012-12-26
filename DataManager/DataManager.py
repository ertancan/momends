__author__ = 'goktan'
from models import Provider
import importlib
from ExternalProviders.BaseProviderWorker import BasePhotoProviderWorker,BaseStatusProviderWorker,BaseLocationProviderWorker
class DataManager:

    def create_momend(self):
        pass

    def collect_user_data(self, user, since, until, inc_photo=True, inc_status=True, inc_checkin=True):
        _user_data = []
        for obj in Provider.objects.all():
            if getattr(user,obj.module_name.lower()+'_set').count()>0:
                worker = self._instantiate_provider_worker(obj)
                if inc_photo and issubclass(worker.__class__,BasePhotoProviderWorker):
                    _user_data = _user_data + worker.collect_photo(user,since,until)
                if inc_status and issubclass(worker.__class__,BaseStatusProviderWorker):
                    _user_data = _user_data + worker.collect_status(user,since,until)
                if inc_checkin and issubclass(worker.__class__,BaseLocationProviderWorker):
                    _user_data = _user_data + worker.collect_checkin(user,since,until)

        return _user_data

    def _instantiate_provider_worker(self, provider):
        mod = importlib.import_module('ExternalProviders.'+provider.package_name+'.'+provider.worker_name,provider.worker_name)
        cl = getattr(mod,provider.worker_name)
        return cl()

