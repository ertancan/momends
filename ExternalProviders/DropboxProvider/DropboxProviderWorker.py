__author__ = 'ertan'

from ExternalProviders.BaseProviderWorker import BasePhotoProviderWorker
from DataManager.models import RawData
from LogManagers.Log import Log
import urllib


class DropboxProviderWorker(BasePhotoProviderWorker):
    def collect_photo(self, user, **kwargs):
        _return_data = []
        if kwargs.get('selected', None):
            _return_data += self.get_selected_photos(user, kwargs['selected'])
        return _return_data

    def get_selected_photos(self, user, selected_photos):
        _collected = []
        _provider = self.getProvider()
        for _photo in selected_photos:
            _url = _photo['link']
            _name = _url[_url.rindex('/')+1:]
            _original_id = urllib.unquote(user.username + _name)
            _raw, _is_new = RawData.objects.get_or_create(original_id=_original_id, provider=_provider,
                                                          defaults={'owner': user, 'type': RawData.DATA_TYPE['Photo'],
                                                                    'original_path': _url})
            if _is_new:
                _raw.title = _name
                _raw.thumbnail = _photo['thumbnail']
            Log.debug('Dropbox photo: ' + str(_raw))
            _collected.append(_raw)
        return _collected

    def get_friendlist(self, user):
        return []
