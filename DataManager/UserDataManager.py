__author__ = 'ertan'
from LogManagers.Log import Log
from models import RawData
from Outputs.AnimationManager.models import CoreAnimationData
from DataManagerModel import DataManagerModel
import random

class UserDataManager(DataManagerModel):
    def __init__(self, enriched_data):
        super(UserDataManager,self).__init__(enriched_data, CoreAnimationData.USER_DATA_KEYWORDS)


    def get_data_for_keyword(self,keyword):
        if keyword in self.keywords:
            index = self.keywords.index(keyword)
            obj_type = index/3
            request_type = index % 3 # 0 getPrevious, 1 getNext, 2 getRand
            if request_type == 0:
                user_data = self.getPreviousData(obj_type)
            elif request_type == 1:
                user_data = self.getNextData(obj_type)
            else:
                user_data = self.getRandData(obj_type)
            self._last_obj = user_data
            return self._last_obj
        return None


    def getPreviousData(self,type):
        if len(self.data[type]) == 0:
            Log.error('No user data for type:'+str(type))
            self._last_obj = None
            return None
        if self.random_indexes[type] != -1:
            self._last_obj = self.data[type][self.random_indexes[type]]
            return self._last_obj
        if self.current_indexes[type] == -1:
            self.current_indexes[type] = 0
        self._last_obj = self.data[type][self.current_indexes[type]]
        return self._last_obj

    def getNextData(self,type):
        self.random_indexes[type] = -1 #Clear previous random index
        if len(self.data[type]) == 0:
            Log.error('No user data for type:'+str(type))
            self._last_obj = None
            return None
        self.current_indexes[type] += 1
        if self.current_indexes[type] == len(self.data[type]):
            self.current_indexes[type] = 0 #For circular theme data
        self._last_obj = self.data[type][self.current_indexes[type]]
        return self._last_obj

    def getRandData(self,type):
        rand_index = random.randint(0,len(self.data[type])-1)
        self.random_indexes[type] = rand_index

        self._last_obj = self.data[type][rand_index]
        return self._last_obj