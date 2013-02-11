__author__ = 'goktan'

from ExternalProviders.BaseProviderWorker import BasePhotoProviderWorker
from DataManager.models import RawData


class FileUploadProviderWorker(BasePhotoProviderWorker):
    def collect_photo(self, user, **kwargs):
        pass