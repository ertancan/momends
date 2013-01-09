__author__ = 'ertan'
from Outputs.AnimationManager.models import ThemeData
from LogManagers.Log import Log
import random

class ThemeDataManager(object):
    def __init__(self,theme):
        theme_assets = ThemeData.objects.filter(theme=theme)
        self.theme_data = self._group_theme_data(theme_assets)
        self.current_indexes = [-1 for i in range(0,len(ThemeData.THEME_DATA_TYPE))] # For -1 array?
        self.random_indexes = [-1 for i in range(0,len(ThemeData.THEME_DATA_TYPE))]


    def _group_theme_data(self,theme_data):
        types = ThemeData.THEME_DATA_TYPE
        result = []
        for i in range(0,len(types)):
            result.append([])

        for data in theme_data:
            result[data.type].append(data)

        return result

    def getPreviousData(self,type):
        if self.random_indexes[type] != -1:
            return self.theme_data[type][self.random_indexes[type]]

        if self.current_indexes[type] == -1:
            self.current_indexes[type] = 0
        return self.theme_data[type][self.current_indexes[type]]

    def getNextData(self,type):
        self.random_indexes[type] = -1 #Clear previous random index
        if len(self.theme_data[type]) == 0:
            Log.error('No theme data for type:'+str(type))
            return None
        self.current_indexes[type] += 1
        if self.current_indexes[type] == len(self.theme_data[type]):
            self.current_indexes[type] = 0 #For circular theme data
        Log.debug('Current index is: '+str(self.current_indexes[type])+' for '+str(type))
        return self.theme_data[type][self.current_indexes[type]]

    def getRandData(self,type):
        rand_index = random.randint(0,len(self.theme_data[type]))
        self.random_indexes[type] = rand_index

        return self.theme_data[type][rand_index]