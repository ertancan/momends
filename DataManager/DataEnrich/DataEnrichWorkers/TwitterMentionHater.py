__author__ = 'ertan'
"""
    Returns 0 for tweets which are direct replies or mentions
    Returns 50 for tweets contains mentions but not starting with mentions
    Returns 100 for others

    --> This enricher is not important for momends with friends, since all items would have mentions in that case;
        However, this will return reduced scores for directly mentioned tweets, consider that!
"""
from BaseDataEnrichWorker import StatusEnrichWorker


class TwitterMentionHater(StatusEnrichWorker):
    def enrich_status(self, raw_data_array):
        _result = []

        for _item in raw_data_array:
        # Base class might remove the item and put a None instead, if it is from an uncompatible provider
            if _item:
                _text = _item.data
                if '@' in _text:
                    if _text.Index('@') == 0:
                        _result.append(0)
                    else:
                        _result.append(50)
                else:
                    _result.append(100)
            else:
                _result.append(None)

        return _result
