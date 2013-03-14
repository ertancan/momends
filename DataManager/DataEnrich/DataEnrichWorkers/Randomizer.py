__author__ = 'ertan'
"""
    Returns a  random score for items
"""
from BaseDataEnrichWorker import StatusEnrichWorker, PhotoEnrichWorker, CheckinEnrichWorker
import random


class Randomizer(StatusEnrichWorker, PhotoEnrichWorker, CheckinEnrichWorker):
    def enrich_status(self, raw_data_array):
        return self._get_random_result_array(raw_data_array)

    def enrich_photo(self, raw_data_array):
        return self._get_random_result_array(raw_data_array)

    def enrich_checkin(self, raw_data_array):
        return self._get_random_result_array(raw_data_array)

    def _get_random_result_array(self, raw_data_array):
        _result_array = []
        for _raw in raw_data_array:
            if _raw:
                _result_array.append(random.randint(1, 100))
            else:
                _result_array.append(None)
        return _result_array
