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

from LogManagers.Log import Log


class DataManagerUtil:
    __metaclass__ = abc.ABCMeta

    @staticmethod
    def download_file(url, name):
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
        os.environ['PATH'] += ':/usr/local/bin'  # TODO: remove this on prod For mac os
        _file_path = settings.THUMBNAIL_FILE_PATH + _output_name
        _save_file_path = settings.SAVE_PREFIX + _file_path
        s = ["convert", _file, '-resize', '500x320^', '-gravity', 'center', '-extent', '500x320', _save_file_path]
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

    @staticmethod
    def send_momend_created_email(momend):
        ctx_dict = {'momend_url': str(reverse_lazy('momends:show-momend', args=('m', momend.cryptic_id))),
                    'owner': momend.owner,
                    'STATIC_URL': settings.STATIC_URL,
                    'HOST_URL': settings.HOST_URL,
                    'start_date': momend.momend_start_date.strftime("%d %B %Y"),
                    'finish_date': momend.momend_end_date.strftime("%d %B %Y")
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
