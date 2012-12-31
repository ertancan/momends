__author__ = 'goktan'
import random
from DataManager.models import RawData,CoreAnimationData
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
        return result

class TemporaryEnrichedObjectHolder(object):
    def __init__(self, raw, criteria, priority):
        self.raw = raw
        self.criteria = criteria
        self.priority = priority