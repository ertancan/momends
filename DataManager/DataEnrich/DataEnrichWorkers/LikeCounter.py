__author__ = 'ertan'
"""
    Returns a score according to the like counts of the items
"""
from BaseDataEnrichWorker import StatusEnrichWorker, PhotoEnrichWorker, CheckinEnrichWorker


class LikeCounter(StatusEnrichWorker, PhotoEnrichWorker, CheckinEnrichWorker):
    def enrich_status(self, raw_data_array):
        return self._get_like_count_array(raw_data_array)

    def enrich_photo(self, raw_data_array):
        return self._get_like_count_array(raw_data_array)

    def enrich_checkin(self, raw_data_array):
        return self._get_like_count_array(raw_data_array)

    def _get_like_count_array(self, raw_data_array):
        _like_count_array = []
        for _raw in raw_data_array:
            if _raw:
                _like_count_array.append(_raw.like_count)
            else:
                _like_count_array.append(None)
        return _like_count_array
