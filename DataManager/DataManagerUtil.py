__author__ = 'goktan'

import urllib2
import abc
from django.conf import settings

class DataManagerUtil:
    __metaclass__ = abc.ABCMeta

    @staticmethod
    def download_file(url, name):
        _file_path = settings.COLLECTED_FILE_PATH + name
        _url = urllib2.urlopen(url)
        with open(_file_path, "wb") as _local_file:
            _local_file.write(_url.read())
        _local_file.close()
        return _file_path

