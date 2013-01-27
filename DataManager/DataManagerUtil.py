__author__ = 'goktan'

import urllib2
import abc
import subprocess
import os
from django.conf import settings
from LogManagers.Log import Log
from django.core.files.storage import default_storage


class DataManagerUtil:
    __metaclass__ = abc.ABCMeta

    @staticmethod
    def get_file2serve(name, params='rb'):
        """
        give a file object from local filesystem or S3 depending to configuration
        """
        if settings.FILE_TARGET == 'S3':
            _local_file = default_storage.open(name, params)
        else:
            _local_file = open(name, params)

        return _local_file

    @staticmethod
    def move_for_serving(file, target):
        """
        move a file from temp place to serving place where this can be filesystem or S3 depending to configuration
        """
        with open(file,'rb') as _local_file:
            _target_file = DataManagerUtil.get_file2serve(target, 'wb')
            _target_file.write(_local_file.read())
            _target_file.close()
            os.remove(file)

    @staticmethod
    def download_file(url, name ):
        """
        Download file from a uri and store it to either tmp dir or default storage defined
        :param url: uri where content will be fetched
        :param name: name of file
        :return:
        """
        _url = urllib2.urlopen(url)
        _file_path = settings.COLLECTED_FILE_PATH + name
        with open(_file_path, 'wb') as _local_file:
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
        s=["convert", _file, '-resize', '500x320^', '-gravity', 'center', '-extent', '500x320', _file_path]
        subprocess.Popen(s).wait()
        return _file_path
