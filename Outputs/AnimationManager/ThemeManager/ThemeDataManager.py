__author__ = 'ertan'
from Outputs.AnimationManager.models import ThemeData
from LogManagers.Log import Log
from DataManager.DataManagerModel import DataManagerModel
import random

class ThemeDataManager(DataManagerModel):
    def __init__(self, theme):
        theme_assets = ThemeData.objects.filter(theme=theme)
        super(ThemeDataManager,self).__init__(self._group_theme_data(theme_assets),ThemeData.THEME_DATA_TYPE_KEYWORDS)


    def _group_theme_data(self,theme_data):
        types = ThemeData.THEME_DATA_TYPE
        result = []
        for i in range(0,len(types)):
            result.append([])

        for data in theme_data:
            result[data.type].append(data)

        return result

    def get_data_for_keyword(self,keyword):
        if keyword in self.keywords:
            index = self.keywords.index(keyword)
            obj_type = index/3
            request_type = index % 3 # 0 getPrevious, 1 getNext, 2 getRand
            if request_type == 0:
                theme_data = self.getPreviousData(obj_type)
            elif request_type == 1:
                theme_data = self.getNextData(obj_type)
            else:
                theme_data = self.getRandData(obj_type)
            self._last_obj = theme_data
            return self._last_obj
        return None

    def getLastResult(self):
        """
        :return: Latest returned result regardless of its type. It may be any of the ThemeData types or None
        """
        return self._last_obj


    def getPreviousData(self,type):
        if len(self.data[type]) == 0:
            Log.error('No theme data for type:'+str(type))
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
            Log.error('No theme data for type:'+str(type))
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