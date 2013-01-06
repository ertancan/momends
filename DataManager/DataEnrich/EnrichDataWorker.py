__author__ = 'goktan'
import random
from Outputs.AnimationManager.models import CoreAnimationData
from LogManagers.Log import Log

class EnrichDataWorker: #TODO keep this as base class and introduce different workers

    def __init__(self, user):
        #collect user info for further usage and use it while choosing data specific for user
        self.user = user

    def enrich_data(self, raw_data_arr): #TODO enrich? :) #TODO Background
        result = []
        for i in range(0,len(CoreAnimationData.USER_DATA_TYPE)/2):
            result.append([])

        for _raw in raw_data_arr:
            tmp = TemporaryEnrichedObjectHolder(raw=_raw, criteria='Random', priority=random.randint(1,100))
            result[_raw.type].append(tmp)
        return self._sort_by_priority(result)

    def _sort_by_priority(self,enriched_data):
        sorted_data = []
        for type_arr in enriched_data:
            Log.debug(type_arr)
            sorted_data.append(sorted(type_arr, key=lambda obj: obj.priority, reverse=True))
        return sorted_data

class TemporaryEnrichedObjectHolder(object):
    def __init__(self, raw, criteria, priority):
        self.raw = raw
        self.criteria = criteria
        self.priority = priority