__author__ = 'goktan'

import abc

class BaseProviderWorker:
    def auth(self):
        pass

class BasePhotoProviderWorker(BaseProviderWorker):
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def collect_photo(self,user,since,until):
        pass

class BaseStatusProviderWorker(BaseProviderWorker):
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def collect_status(self,user,since,until):
        pass

class BaseLocationProviderWorker(BaseProviderWorker):
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def collect_checkin(self,user,since,until):
        pass
