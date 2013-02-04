__author__ = 'goktan'
import random
from Outputs.AnimationManager.models import CoreAnimationData
from LogManagers.Log import Log
from DataManager.models import Momend
from DataManager.models import User

class EnrichDataWorker: #TODO keep this as base class and introduce different workers

    @staticmethod
    def enrich_user_raw_data(raw_data_arr): #TODO enrich? :) #TODO Background
        """get list of user raw data smartly according to its relevance to user.
        Args:
            raw_data_array: raw data array to get enhanced to

        Returns:
            an array of ordered raw data (aka. enhanced data)
        """
        result = []
        for i in range(0,len(CoreAnimationData.USER_DATA_KEYWORDS)/2):
            result.append([])

        for _raw in raw_data_arr:
            tmp = TemporaryEnrichedObjectHolder(raw=_raw, criteria='Random', priority=random.randint(1,100))
            result[_raw.type].append(tmp)
        return EnrichDataWorker._sort_by_priority(result)

    @staticmethod
    def get_related_momends(momend, max_count, get_private=True):
        """get list of top momends for a specific user
        Args:
            momend: momend to set reference for related momends
            max_count: maximum momend number to return
            get_private: if True, then include the private momends to the result

        Returns:
            an array of curated related momends
        """
        _obj = Momend.objects.filter(owner=momend.owner)
        if not get_private:
            _obj = _obj.filter(privacy=Momend.PRIVACY_CHOICES['Public'])
        _obj = _obj.order_by('?').reverse()
        return _obj if (_obj.count() < max_count) else _obj[_obj.count() - max_count:]


    @staticmethod
    def _sort_by_priority(enriched_data):
        sorted_data = []
        for type_arr in enriched_data:
            sorted_data.append(sorted(type_arr, key=lambda obj: obj.priority, reverse=True))
        Log.debug('Sorted data:'+str(sorted_data))
        return sorted_data

    @staticmethod
    def get_top_user_momends(user, max_count, get_private=True): #TODO (goktan): here we need an algorithm
        """get list of top momends for a specific user
        Args:
            user: user to get momend
            max_count: maximum momend number to return
            get_private: if True, then include the private momends to the result

        Returns:
            an array of curated top user momends
        """
        _obj = Momend.objects.filter(owner=user)
        if not get_private:
            _obj = _obj.filter(privacy=Momend.PRIVACY_CHOICES['Public'])
        _obj = _obj.order_by('?').reverse()
        return _obj if (_obj.count() < max_count) else _obj[_obj.count() - max_count:]

    @staticmethod
    def get_top_public_momends(max_count):
        """get lit of top public moments
        Args:
            max_count: maximum momend number to return

        Returns:
            an array of curated top public momends
        """
        _obj = Momend.objects.filter(privacy=Momend.PRIVACY_CHOICES['Public']).order_by('create_date').reverse()

        return _obj if (_obj.count() < max_count) else _obj[_obj.count() - max_count:]

    @staticmethod
    def get_latest_user_momends(user, max_count, get_private=True):
        """get list of users latest momends
        Args:
            user: user to get momend
            max_count: maximum momend number to return
            get_private: if True, then include the private momends to the result

        Returns:
            an array of curated top user momends
        """
        _obj = Momend.objects.filter(owner=user)
        if not get_private:
            _obj = _obj.filter(privacy=Momend.PRIVACY_CHOICES['Public'])
        _obj = _obj.order_by('create_date').reverse()
        return _obj if (_obj.count() < max_count) else _obj[_obj.count() - max_count:]


class TemporaryEnrichedObjectHolder(object):
    def __init__(self, raw, criteria, priority):
        self.raw = raw
        self.criteria = criteria
        self.priority = priority

    def __str__(self):
        return str(self.raw)+'='+self.criteria+':'+str(self.priority)

    def __repr__(self):
        return self.__str__()