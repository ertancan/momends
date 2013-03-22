__author__ = 'ertan'
"""
    Returns the assigned values for the hashtags in the list (Average of hashtags if more than one),
    Return 50 to unknown hashtags
"""
from BaseDataEnrichWorker import StatusEnrichWorker
import re


class TwitterHashtagRanker(StatusEnrichWorker):
    HASHTAGS = {'#FF': 0,  # TODO add more hashtags
                '#MessageMe': 0,
                '#happy': 100, }

    def enrich_status(self, raw_data_array):
        _result = []
        _hashtag_re = '(\\#(?:[a-z0-9_]*))'
        _hashtag_finder = re.compile(_hashtag_re, re.IGNORECASE | re.DOTALL)

        for _item in raw_data_array:
        # Base class might remove the item and put a None instead, if it is from an uncompatible provider
            if _item:
                _hashtag_count = 0
                _hashtag_score_total = 0
                _text = _item.data

                _hashtag = _hashtag_finder.search(_text)
                while _hashtag:  # For every hashtag
                    _tag = _hashtag.group()
                    if _tag in TwitterHashtagRanker.HASHTAGS:
                        _hashtag_count += 1
                        _hashtag_score_total += TwitterHashtagRanker.HASHTAGS[_tag]
                    _text = _text.replace(_tag, '')
                    _hashtag = _hashtag_finder.search(_text)

                if _hashtag_count > 0:
                    _result.append(_hashtag_score_total / (_hashtag_count + 0.0))
                else:
                    _result.append(50)
            else:
                _result.append(None)

        return _result
