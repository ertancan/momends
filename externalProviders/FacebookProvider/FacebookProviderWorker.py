__author__ = 'goktan'

from ExternalProviders.BaseProviderWorker import BaseLocationProviderWorker,BasePhotoProviderWorker,BaseStatusProviderWorker
from models import FacebookProviderModule
from DataManager.models import RawData
import facebook

class FacebookProviderWorker(BasePhotoProviderWorker, BaseStatusProviderWorker, BaseLocationProviderWorker): #TODO not collecting location!
    def collect_photo(self,user,since,until):
        access_token=self._get_access_token(user)
        api = facebook.GraphAPI(access_token)

        provider = self.getProvider()

        result=api.get_connections('me', 'photos', limit=200, since=str(since), until=str(until),
            fields = 'likes.limit(500),comments.limit(500),source,name,sharedposts')
        _raw_data= []
        for obj in result['data']:
            _raw = RawData()
            _raw.type=RawData.DATA_TYPE['Photo']
            _raw.source = provider
            _raw.path = obj['source']
            _raw.data = obj['name']
            _raw.like_count = len(obj['likes'])
            _raw.share_count = len(obj['sharedposts'])
            _raw.comment_count = len(obj['comments'])
            _raw.create_date = obj['created_time']
            _raw.original_id = obj['id']
            _raw_data.append(_raw)

        return _raw_data

    def collect_status(self, user, since, until):
        access_token=self._get_access_token(user)
        api = facebook.GraphAPI(access_token)

        provider = self.getProvider()

        result=api.get_connections('me', 'statuses', limit=200, since=str(since), until=str(until),
            fields='id,message,likes.limit(500),comments.limit(500),sharedposts,updated_time')

        _raw_data= []
        for obj in result['data']:
            _raw = RawData()
            _raw.type=RawData.DATA_TYPE['Status']
            _raw.source = provider
            _raw.data = obj['message']
            _raw.like_count = len(obj['likes'])
            _raw.share_count = len(obj['sharedposts'])
            _raw.comment_count = len(obj['comments'])
            _raw.create_date = obj['updated_time']
            _raw.original_id = obj['id']
            _raw_data.append(_raw)

        return _raw_data


    def collect_checkin(self,user,since,until):
        access_token=self._get_access_token(user)
        api = facebook.GraphAPI(access_token)
        result=api.get_connections('me', 'checkins', limit=200, since=str(since), until=str(until),
            fields='id,place,likes.limit(500),comments.limit(500),created_time') #TODO hardcoded limits will go to config file
        provider = self.getProvider()

        _raw_data= []
        for obj in result['data']:
            _raw = RawData()
            _raw.type = RawData.DATA_TYPE['Checkin']
            _raw.source = provider
            _raw.data = obj['place']['name']
            _raw.like_count = len(obj['likes'])
            _raw.comment_count = len(obj['comments'])
            _raw.create_date = obj['created_time']
            _raw.original_id = obj['id']
            _raw_data.append(_raw)

        return _raw_data

def _get_access_token(self, user):
        #TODO obtain access token and return
        _obj = FacebookProviderModule.objects.get(owner=user)
        return _obj.token