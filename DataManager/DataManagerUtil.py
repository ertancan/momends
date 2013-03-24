__author__ = 'goktan'

import urllib2
import abc
import subprocess
import os
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.core.urlresolvers import reverse_lazy
from django.core.files.storage import default_storage

from LogManagers.Log import Log


class DataManagerUtil:
    __metaclass__ = abc.ABCMeta

    @staticmethod
    def download_data_to_tmp(url, name, upload_to_cloud=True):
        """
        Download file from an uri
        :param url: uri where content will be fetched
        :param name: name of file
        :return: file path to local file
        """
        _url_connection = urllib2.urlopen(url)
        _file_path = settings.COLLECTED_FILE_PATH + name
        _save_file_path = settings.TMP_FILE_PATH + _file_path

        _url_content = _url_connection.read()
        _url_connection.close()

        with open(_save_file_path, 'w+') as _local_file:
            _local_file.write(_url_content)
        _local_file.close()

        if upload_to_cloud:
            _s3_file = default_storage.open(_file_path, 'w+')
            _s3_file.write(_url_content)
            _s3_file.close()

        return _save_file_path

    @staticmethod
    def fetch_collected_data_from_s3(file):
        _s3_file = default_storage.open(file, 'r')
        _tmp_filename = settings.TMP_FILE_PATH + file
        with open(_tmp_filename, 'w+') as _tmp_file:
            _tmp_file.write(_s3_file.read())
        _s3_file.close()
        _tmp_file.close()
        return _tmp_filename

    @staticmethod
    def prepare_raw_data(raw):
        if not raw.data:
            try:
                _dot_index = raw.original_path.rindex('.')
                _ext_part = raw.original_path[_dot_index:]
            except ValueError:
                _ext_part = '.jpg'
            return DataManagerUtil.download_data_to_tmp(raw.original_path, str(raw)+_ext_part)
        else:
            return DataManagerUtil.fetch_collected_data_from_s3(raw.data)

    @staticmethod
    def upload_data_to_s3(filename, prefix=None):
        _s3_filename = filename
        if filename.startswith(settings.TMP_FILE_PATH):
            _s3_filename = filename.replace(settings.TMP_FILE_PATH, '')
        if prefix:
            _s3_filename = prefix + _s3_filename
        _s3_file = default_storage.open(_s3_filename, 'w+')
        with open(filename) as _tmp_file:
            _s3_file.write(_tmp_file.read())
        _s3_file.close()
        _tmp_file.close()
        return _s3_filename

    @staticmethod
    def create_photo_thumbnail(_file, _output_name):
        if not _file:
            Log.error('Error while creating thumbnail (No file given)')
            return
        os.environ['PATH'] += ':/usr/local/bin'  # TODO: remove this on prod For mac os
        _file_path = settings.THUMBNAIL_FILE_PATH + _output_name
        _save_file_path = settings.TMP_FILE_PATH + _file_path
        s = ["convert", _file.local_path, '-resize', '500x320^', '-gravity', 'center', '-extent', '500x320', _save_file_path]
        subprocess.Popen(s).wait()
        DataManagerUtil.upload_data_to_s3(_save_file_path)
        os.remove(_save_file_path)
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
        _save_file_path = settings.TMP_FILE_PATH + _file_path
        with open(_save_file_path, 'w+') as _local_file:
            for chunk in content.chunks():
                _local_file.write(chunk)
            _local_file.close()
        return _file_path

    @staticmethod
    def send_momend_created_email(momend):
        ctx_dict = {'momend_url': str(reverse_lazy('momends:show-momend', args=('m', momend.cryptic_id))),
                    'owner': momend.owner,
                    'STATIC_URL': settings.STATIC_URL,
                    'HOST_URL': settings.HOST_URL,
                    'start_date': momend.momend_start_date.strftime("%d %h %Y"),
                    'finish_date': momend.momend_end_date.strftime("%d %h %Y")
                    }
        subject = render_to_string('MomendCreatedMailSubjectTemplate.html', ctx_dict)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())

        message = render_to_string('MomendCreatedMailTemplate.html', ctx_dict)
        text_content = strip_tags(message)
        msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [momend.owner.email])
        msg.attach_alternative(message, "text/html")
        try:
            msg.send()
            return True
        except Exception as e:
            Log.error('Error while sending momend created email: '+str(e))
            return False

    @staticmethod
    def send_share_email(sender, receivers, url):
        sender_name = 'someone'
        if not sender.is_anonymous():
            sender_name = sender.get_full_name() + ' ('+sender.email+')'
        ctx_dict = {'momend_url': url,
                    'sender': sender_name,
                    'STATIC_URL': settings.STATIC_URL,
                    'HOST_URL': settings.HOST_URL
                    }
        subject = render_to_string('MomendShareMailSubjectTemplate.html', ctx_dict)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())

        message = render_to_string('MomendShareMailTemplate.html', ctx_dict)
        text_content = strip_tags(message)
        msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, receivers)
        msg.attach_alternative(message, "text/html")
        try:
            msg.send()
            return True
        except Exception as e:
            Log.error('Error while sending momend share email: '+str(e))
            return False


class CloudFile(object):
    cloud_dirty = False
    enhanced_dirty = False

    def __init__(self, raw):
        self.raw = raw
        self.local_url = None
        self.cloud_url = raw.data
        self.enhanced_path = None

    @property
    def local_path(self):
        if self.local_url:
            return self.local_url
        if self.cloud_url:
            try:
                self.local_url = DataManagerUtil.fetch_collected_data_from_s3(self.cloud_url)
                return self.local_url
            except Exception as e:
                Log.error('Exception occurred while downloading file from cloud. Trying to download from provider. :' + str(e))

        # Not downloaded anywhere yet or exception occured above
        if '.' in self.raw.original_path:
            _dot_index = self.raw.original_path.rindex('.')
            _ext_part = self.raw.original_path[_dot_index:]
        else:
            _ext_part = '.jpg'
        self.local_url = DataManagerUtil.download_data_to_tmp(self.raw.original_path, str(self.raw) + _ext_part)
        self.cloud_dirty = True
        return self.local_url

    def set_enhanced(self, enhanced_path):
        if self.enhanced_path == enhanced_path:
            return
        self.enhanced_path = enhanced_path
        self.enhanced_dirty = True

    def commit(self):
        if self.enhanced_dirty:
            try:
                _old_file = self.enhanced_path
                self.enhanced_path = settings.S3_URL + DataManagerUtil.upload_data_to_s3(self.enhanced_path)
                self.enhanced_dirty = False
                os.remove(_old_file)
            except Exception as e:
                Log.error('Error occurred while uploading enhanced data. :' + str(e))
        if self.cloud_dirty:
            try:
                self.cloud_url = DataManagerUtil.upload_data_to_s3(self.local_url)
                self.raw.data = self.cloud_url
                self.raw.save()
                self.cloud_dirty = False
            except Exception as e:
                Log.error('Error occurred while uploading collected data. :' + str(e))
        if not self.cloud_url:  # Will be used without enhancements so not downloaded yet
            self.cloud_url = DataManagerUtil.upload_data_to_s3(self.local_path)  # local_path will download then upload_data_to_s3 will upload back
            self.raw.data = self.cloud_url
            self.raw.save()

    def clean_local(self):  # TODO clean enhanced here
        if self.local_url:
            try:
                os.remove(self.local_url)
            except:
                Log.error('Couldnot delete local tmp')
