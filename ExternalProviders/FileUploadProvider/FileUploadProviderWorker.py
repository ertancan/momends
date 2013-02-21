__author__ = 'goktan'

from ExternalProviders.BaseProviderWorker import BasePhotoProviderWorker
from DataManager.models import RawData
from DataManager.DataManagerUtil import DataManagerUtil
from django.conf import settings


class FileUploadProviderWorker(BasePhotoProviderWorker):
    def collect_photo(self, user, **kwargs):
        _files = kwargs['files']

        for _file in _files:
            _raw = RawData()
            _raw.original_id = RawData.key_generate
            _raw.owner = user
            _raw.provider = self.getProvider()
            _raw.title =  str(_file)
            _raw.data = DataManagerUtil.create_file(file, str(_raw))

            _raw.type = RawData.DATA_TYPE['Photo']


            _raw.save()