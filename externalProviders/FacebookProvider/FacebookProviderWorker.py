__author__ = 'goktan'

from ExternalProviders.BaseProviderWorker import BaseLocationProviderWorker,BasePhotoProviderWorker,BaseStatusProviderWorker
from models import FacebookProviderModule
from DataManager.models import RawData
import datetime
import facebook
import pytz

class FacebookProviderWorker(BasePhotoProviderWorker, BaseStatusProviderWorker, BaseLocationProviderWorker): #TODO not collecting location!
    def collect_photo(self,user,since,until):
        access_token=self._get_access_token(user)
        api = facebook.GraphAPI(access_token)

        provider = self.getProvider()

        result=api.get_connections('me', 'photos', limit=200, since=str(since), until=str(until),
            fields = 'likes.limit(500),comments.limit(500),source,name,sharedposts')
        _return_data= []
        for obj in result['data']:
            _raw = RawData()
            _raw.owner = user
            _raw.type=RawData.DATA_TYPE['Photo']
            _raw.source = provider
            _raw.path = obj['source']
            if 'name' in obj:
                _raw.data = obj['name']
            if 'likes' in obj:
                _raw.like_count = len(obj['likes'])
            if 'sharedposts' in obj:
                _raw.share_count = len(obj['sharedposts'])
            if 'comments' in obj:
                _raw.comment_count = len(obj['comments'])
            _raw.create_date = datetime.datetime.strptime(obj['created_time'],'%Y-%m-%dT%H:%M:%S+0000').replace(tzinfo=pytz.UTC)
            _raw.original_id = obj['id']
            _return_data.append(_raw)

        return _return_data

    def collect_status(self, user, since, until):
        access_token=self._get_access_token(user)
        api = facebook.GraphAPI(access_token)

        provider = self.getProvider()

        result=api.get_connections('me', 'statuses', limit=200, since=str(since), until=str(until),
            fields='id,message,likes.limit(500),comments.limit(500),sharedposts,updated_time')

        _return_data= []
        for obj in result['data']:
            _raw = RawData()
            _raw.owner = user
            _raw.type=RawData.DATA_TYPE['Status']
            _raw.source = provider
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

        return _return_data


    def collect_checkin(self, user, since, until):
        access_token=self._get_access_token(user)
        api = facebook.GraphAPI(access_token)
        result=api.get_connections('me', 'checkins', limit=200, since=str(since), until=str(until),
            fields='id,place,likes.limit(500),comments.limit(500),created_time') #TODO hardcoded limits will go to config file
        provider = self.getProvider()

        _return_data= []
        for obj in result['data']:
            _raw = RawData()
            _raw.owner = user
            _raw.type = RawData.DATA_TYPE['Checkin']
            _raw.source = provider
            _raw.data = obj['place']['name']
            if 'likes' in obj:
                _raw.like_count = len(obj['likes'])
            if 'comments' in obj:
                _raw.comment_count = len(obj['comments'])
            _raw.create_date = datetime.datetime.strptime(obj['created_time'],'%Y-%m-%dT%H:%M:%S+0000').replace(tzinfo=pytz.UTC)
            _raw.original_id = obj['id']
            _return_data.append(_raw)

        return _return_data

    def _get_access_token(self, user):
        #TODO obtain access token and return
        _obj = FacebookProviderModule.objects.get(owner=user)
        return _obj.token