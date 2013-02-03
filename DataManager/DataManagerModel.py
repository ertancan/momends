__author__ = 'ertan'
from models import RawData
import abc

class DataManagerModel(object):
    def __init__(self, data):
        self.data = data
        self.current_indexes = [-1 for i in range(0,len(RawData.DATA_TYPE))] # For -1 array?
        self.random_indexes = [-1 for i in range(0,len(RawData.DATA_TYPE))]
        self._last_obj = None
        self.keywords = abc.abstractproperty


    def getLastResult(self):
        """
        :return: Latest returned result regardless of its type. It may be any of the ThemeData types or None
        """
        return self._last_obj

    @abc.abstractmethod
    def get_data_for_keyword(self,keyword):
        """
        Returns the related object for given keyword
        :param keyword: like {{NEXT_THEME_DATA}} etc.
        :return: object or None
        """
        pass

    @abc.abstractmethod
    def getPreviousData(self,type):
        pass

    @abc.abstractmethod
    def getNextData(self,type):
        pass

    @abc.abstractmethod
    def getRandData(self,type):
        pass