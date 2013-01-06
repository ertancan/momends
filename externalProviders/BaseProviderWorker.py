__author__ = 'goktan'

import abc
from DataManager.models import Provider
from social_auth.db.django_models import UserSocialAuth
from LogManagers.Log import Log

class BaseProviderWorker(object):
    def auth(self):
        pass

    def getProvider(self):
        Log.debug( self.__class__.__name__)
        return Provider.objects.get(worker_name=self.__class__.__name__)

class BasePhotoProviderWorker(BaseProviderWorker):
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def collect_photo(self, user, since, until):
        pass
    @abc.abstractmethod
    def _fetch_photo(self, id, name):
        pass

class BaseStatusProviderWorker(BaseProviderWorker):
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def collect_status(self, user, since, until):
        pass

class BaseLocationProviderWorker(BaseProviderWorker):
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def collect_checkin(self, user, since, until):
        pass
