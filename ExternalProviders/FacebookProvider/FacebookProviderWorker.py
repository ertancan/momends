__author__ = 'goktan'

from ExternalProviders.BaseProviderWorker import BaseLocationProviderWorker
from ExternalProviders.BaseProviderWorker import BasePhotoProviderWorker
from ExternalProviders.BaseProviderWorker import BaseStatusProviderWorker
from DataManager.models import RawData
import datetime
import facebook
import pytz
from LogManagers.Log import Log
from social_auth.db.django_models import UserSocialAuth
from DataManager.DataManagerUtil import DataManagerUtil
from django.conf import settings

class FacebookProviderWorker(BasePhotoProviderWorker, BaseStatusProviderWorker, BaseLocationProviderWorker): #TODO not collecting location!
    def collect_photo(self, user, since, until):
        access_token=self._get_access_token(user)
        api = facebook.GraphAPI(access_token)
        provider = self.getProvider()
        try:
            result=api.get_connections('me', 'photos', limit=200, since=str(since), until=str(until),
                fields = 'likes.limit(500),comments.limit(500),source,name,sharedposts,images')
        except:
            return None
        _return_data= []
        for obj in result['data']:
            if not RawData.objects.filter(original_id=obj['id']).filter(provider=provider).exists():
                _raw = RawData()
                _raw.original_id = obj['id']
                _raw.owner = user
                _raw.type=RawData.DATA_TYPE['Photo']
                _raw.provider = provider
                _raw.original_path = obj['images'][0]['source']
                if 'name' in obj:
                    _raw.title = obj['name']
                if 'likes' in obj:
                    _raw.like_count = len(obj['likes'])
                if 'sharedposts' in obj:
                    _raw.share_count = len(obj['sharedposts'])
                if 'comments' in obj:
                    _raw.comment_count = len(obj['comments'])
                _raw.create_date = datetime.datetime.strptime(obj['created_time'],'%Y-%m-%dT%H:%M:%S+0000').replace(tzinfo=pytz.UTC)
                #TODO error handling (goktan)
                try:
                    _dot_index = _raw.original_path.rindex('.')
                    _ext_part = _raw.original_path[_dot_index:]
                except ValueError:
                    _ext_part = '.jpg'
                _raw.data = DataManagerUtil.download_file(_raw.original_path, str(_raw)+_ext_part)
                _raw.thumbnail = DataManagerUtil.create_photo_thumbnail(settings.SAVE_PREFIX + _raw.data, str(_raw)+ '_thumb'+ _ext_part)
                Log.debug(_raw)
            else:
                _raw = RawData.objects.filter(original_id=obj['id']).get(provider=provider)
                Log.debug(_raw.original_id + ' found in DB')
            _return_data.append(_raw)

        return _return_data

    def collect_status(self, user, since, until):
        access_token=self._get_access_token(user)
        api = facebook.GraphAPI(access_token)
        provider = self.getProvider()
        try:
            result=api.get_connections('me', 'statuses', limit=200, since=str(since), until=str(until),
                fields='id,message,likes.limit(500),comments.limit(500),sharedposts,updated_time')
        except:
            return None
        _return_data= []
        for obj in result['data']:
            if not RawData.objects.filter(original_id=obj['id']).filter(provider=provider).exists():
                _raw = RawData()
                _raw.owner = user
                _raw.type=RawData.DATA_TYPE['Status']
                _raw.provider = provider
                _raw.data = obj['message']
                if 'likes' in obj:
                    _raw.like_count = len(obj['likes'])
                if 'sharedposts' in obj:
                    _raw.share_count = len(obj['sharedposts'])
                if 'comments' in obj:
                    _raw.comment_count = len(obj['comments'])
                _raw.create_date = datetime.datetime.strptime(obj['updated_time'],'%Y-%m-%dT%H:%M:%S+0000').replace(tzinfo=pytz.UTC)
                _raw.original_id = obj['id']
                _return_data.append(_raw)
            else:
                _raw = RawData.objects.filter(original_id=obj['id']).get(provider=provider)
                Log.debug( _raw.original_id + ' found in DB')
        return _return_data

    def collect_checkin(self, user, since, until):
        access_token=self._get_access_token(user)
        api = facebook.GraphAPI(access_token)
        try:
            result=api.get_connections('me', 'checkins', limit=200, since=str(since), until=str(until),
                fields='id,place,likes.limit(500),comments.limit(500),created_time') #TODO hardcoded limits will go to config file
        except:
            return None

        provider = self.getProvider()

        _return_data= []
        for obj in result['data']:
            if not RawData.objects.filter(original_id=obj['id']).filter(provider=provider).exists():
                _raw = RawData()
                _raw.owner = user
                _raw.type = RawData.DATA_TYPE['Checkin']
                _raw.provider = provider
                _raw.data = obj['place']['name']
                if 'likes' in obj:
                    _raw.like_count = len(obj['likes'])
                if 'comments' in obj:
                    _raw.comment_count = len(obj['comments'])
                _raw.create_date = datetime.datetime.strptime(obj['created_time'],'%Y-%m-%dT%H:%M:%S+0000').replace(tzinfo=pytz.UTC)
                _raw.original_id = obj['id']
                _return_data.append(_raw)
            else:
                _raw = RawData.objects.filter(original_id=obj['id']).get(provider=provider)
                Log.debug( _raw.original_id + ' found in DB')
        return _return_data

    def _get_access_token(self, user):
        _instance = UserSocialAuth.objects.filter(provider='facebook').get(user=user)
        return  _instance.tokens['access_token']

