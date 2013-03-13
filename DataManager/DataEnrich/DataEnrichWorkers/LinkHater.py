__author__ = 'ertan'
"""
    Status enricher:
    Returns reduced priority for statuses containing links
"""
from BaseDataEnrichWorker import StatusEnrichWorker


class LinkHater(StatusEnrichWorker):
    def enrich_status(self, raw_data_array):
        _result = []

        for _item in raw_data_array:
        # Base class might remove the item and put a None instead, if it is from an uncompatible provider
            if _item:
                _text = _item.data
                if 'http://' in _text or 'https://' in _text:
                    _result.append(0)
                else:
                    _result.append(100)
            else:
                _result.append(None)

        return _result
