__author__ = 'goktan'

from ExternalProviders.BaseProviderWorker import BaseLocationProviderWorker,BasePhotoProviderWorker,BaseStatusProviderWorker
from models import FacebookProviderModule
import facebook

class FacebookProviderWorker(BasePhotoProviderWorker,BaseStatusProviderWorker,BaseLocationProviderWorker):
    def collect_photo(self,user,since,until):
        access_token=self._get_access_token(user)
        api = facebook.GraphAPI(access_token)
        result=api.get_connections('me','photos',limit=200,since=str(since),until=str(until))

        for obj in result['data']:
            print str(obj)

    def collect_status(self,user,since,until):
        access_token=self._get_access_token(user)
        api = facebook.GraphAPI(access_token)
        result=api.get_connections('me','statuses',limit=200,since=str(since),until=str(until))

        for obj in result['data']:
            print str(obj)


    def collect_checkin(self,user,since,until):
        access_token=self._get_access_token(user)
        api = facebook.GraphAPI(access_token)
        result=api.get_connections('me','checkins',limit=200,since=str(since),until=str(until))

        for obj in result['data']:
            print str(obj)

    def _get_access_token(self,user):
        #TODO obtain access token and return
        _obj = FacebookProviderModule.objects.get(owner=user)
        return _obj.token