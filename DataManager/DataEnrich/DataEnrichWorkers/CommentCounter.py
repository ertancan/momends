__author__ = 'ertan'
"""
    Returns a score according to the comment counts of the items
"""
from BaseDataEnrichWorker import StatusEnrichWorker, PhotoEnrichWorker, CheckinEnrichWorker


class CommentCounter(StatusEnrichWorker, PhotoEnrichWorker, CheckinEnrichWorker):
    def enrich_status(self, raw_data_array):
        return self._get_comment_count_array(raw_data_array)

    def enrich_photo(self, raw_data_array):
        return self._get_comment_count_array(raw_data_array)

    def enrich_checkin(self, raw_data_array):
        return self._get_comment_count_array(raw_data_array)

    def _get_comment_count_array(self, raw_data_array):
        _max_like = 1  # Prevent divide by 0
        for _raw in raw_data_array:
            if _raw and _raw.comment_count > _max_like:
                _max_like = _raw.comment_count
        _max_like *= 1.0  # for float division
        _comment_count_array = []
        for _raw in raw_data_array:
            if _raw:
                _comment_count_array.append((_raw.comment_count/_max_like) * 100)
            else:
                _comment_count_array.append(None)
        return _comment_count_array
