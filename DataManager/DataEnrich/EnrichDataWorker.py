__author__ = 'goktan'
import random
from DataManager.models import RawData
class EnrichDataWorker: #TODO keep this as base class and introduce different workers

    def __init__(self, user):
        #collect user info for further usage and use it while choosing data specific for user
        self.user = user

    def enrich_data(self, raw_data_arr): #TODO enrich? :) #TODO Background
        result = {'photo': [], 'status': [], 'checkin': [], 'background': []}
        for _raw in raw_data_arr:
            tmp = TemporaryEnrichedObjectHolder(raw=_raw, criteria='Random', priority=random.randint(1,100))
            if _raw.type == RawData.DATA_TYPE['Photo']:
                result['photo'].append(tmp)
            elif _raw.type == RawData.DATA_TYPE['Status']:
                result['status'].append(tmp)
            elif _raw.type == RawData.DATA_TYPE['Checkin']:
                result['checkin'].append(tmp)
        return result

class TemporaryEnrichedObjectHolder(object):
    def __init__(self, raw, criteria, priority):
        self.raw = raw
        self.criteria = criteria
        self.priority = priority