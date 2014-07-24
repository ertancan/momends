__author__ = 'ertan'
import abc
from DataManager.models import RawData
from LogManagers.Log import Log


class BaseDataEnrichWorker(object):
    def enrich_status(self, raw_data_array):
        Log.info('You asked me( ' + self.__class__.__name__ + ' ) to enrich --Status--, but I cannot')
        return []

    def enrich_photo(self, raw_data_array):
        Log.info('You asked me( ' + self.__class__.__name__ + ' ) to enrich --Photo--, but I cannot')
        return []

    def enrich_checkin(self, raw_data_array):
        Log.info('You asked me( ' + self.__class__.__name__ + ' ) to enrich --Checkin--, but I cannot')
        return []

    def enrich(self, raw_data_array, enrich_type, provider_filter):
        _filtered_data = []  # Pass only compatible providers' data to workers
        for _raw in raw_data_array:
            if _raw.provider in provider_filter:
                _filtered_data.append(_raw)
            else:
                _filtered_data.append(None)

        if enrich_type == RawData.DATA_TYPE['Status']:
            return self.enrich_status(_filtered_data)
        elif enrich_type == RawData.DATA_TYPE['Photo']:
            return self.enrich_photo(_filtered_data)
        elif enrich_type == RawData.DATA_TYPE['Checkin']:
            return self.enrich_checkin(_filtered_data)


class StatusEnrichWorker(BaseDataEnrichWorker):
    @abc.abstractmethod
    def enrich_status(self, raw_data_array):
        pass


class PhotoEnrichWorker(BaseDataEnrichWorker):
    @abc.abstractmethod
    def enrich_photo(self, raw_data_array):
        pass


class CheckinEnrichWorker(BaseDataEnrichWorker):
    @abc.abstractmethod
    def enrich_checkin(self, raw_data_array):
        pass
