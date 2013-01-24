__author__ = 'goktan'

import urllib2
import abc
import subprocess
import os
from django.conf import settings
from LogManagers.Log import Log

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

    @staticmethod
    def create_photo_thumbnail(_file, _output_name):
        if not _file:
            Log.error('Error while creating thumbnail (No file given)')
            return
        os.environ['PATH'] += ':/usr/local/bin' #TODO: remove this on prod For mac os

        _file_path = settings.THUMBNAIL_FILE_PATH + _output_name
        s=["convert", _file, '-resize', '500x500', _file_path]
        print s
        subprocess.Popen(s)
        return _file_path
