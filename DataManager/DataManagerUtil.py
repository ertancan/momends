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
    def download_file(url, name ):
        """
        Download file from an uri
        :param url: uri where content will be fetched
        :param name: name of file
        :return: file path to local file
        """
        _url = urllib2.urlopen(url)
        _file_path = settings.COLLECTED_FILE_PATH + name
        _save_file_path = settings.SAVE_PREFIX + _file_path

        with open(_save_file_path, 'wb+') as _local_file:
            _local_file.write(_url.read())
        _local_file.close()
        return _file_path

    @staticmethod
    def download_raw_data(raw):
        try:
            _dot_index = raw.original_path.rindex('.')
            _ext_part = raw.original_path[_dot_index:]
        except ValueError:
            _ext_part = '.jpg'
        return DataManagerUtil.download_file(raw.original_path, str(raw)+_ext_part)

    @staticmethod
    def create_photo_thumbnail(_file, _output_name):
        if not _file:
            Log.error('Error while creating thumbnail (No file given)')
            return
        os.environ['PATH'] += ':/usr/local/bin' #TODO: remove this on prod For mac os
        _file_path = settings.THUMBNAIL_FILE_PATH + _output_name
        _save_file_path = settings.SAVE_PREFIX + _file_path
        s=["convert", _file, '-resize', '500x320^', '-gravity', 'center', '-extent', '500x320', _save_file_path]
        subprocess.Popen(s).wait()
        return _file_path

    @staticmethod
    def create_file(content, name):
        """
        Save content to a file
        :param content: content of file to save
        :param name: name of file
        :return: file path to local file
        """
        _file_path = settings.COLLECTED_FILE_PATH + name
        _save_file_path = settings.SAVE_PREFIX + _file_path
        with open(_save_file_path, 'wb+') as _local_file:
            for chunk in content.chunks():
                _local_file.write(chunk)
            _local_file.close()
        return _file_path