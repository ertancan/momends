__author__ = 'goktan'

import abc
from DataManager.models import Provider
from LogManagers.Log import Log


class BaseProviderWorker(object):

    def getProvider(self):
        Log.debug(self.__class__.__name__)
        return Provider.objects.get(worker_name=self.__class__.__name__)

    def filter_for_friends(self, data_list, friend_list):
        """
            Filters given RawData array for given list of friend id's
            Filters by original used ids of friends (e.g. facebook id by filtering facebook friends)
            @param data_list: RawData array
            @param friend_list: Array of friend ids.  # TODO accept django user objects, too
        """
        _result_array = []
        if len(friend_list) == 0:
            return _result_array

        Log.debug(str(friend_list))
        for _raw in data_list:
            if not _raw.tags:
                continue
            tag_list = _raw.tags.split(',')
            Log.debug(_raw.tags)
            for _friend in friend_list:
                if _friend in tag_list:
                    _result_array.append(_raw)
                    break
        return _result_array

    @abc.abstractmethod
    def get_friendlist(self, user, **kwargs):
        pass


class BasePhotoProviderWorker(BaseProviderWorker):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def collect_photo(self, user, **kwargs):
        pass


class BaseStatusProviderWorker(BaseProviderWorker):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def collect_status(self, user, **kwargs):
        pass


class BaseLocationProviderWorker(BaseProviderWorker):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def collect_checkin(self, user, **kwargs):
        pass
