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


class FacebookProviderWorker(BasePhotoProviderWorker, BaseStatusProviderWorker, BaseLocationProviderWorker):
    def collect_photo(self, user, **kwargs):
        _return_data = []  # TODO exceptions here if cannot connect to facebook
        if kwargs['is_date']:
            _return_data += self._collect_photo_by_date(user, kwargs['since'], kwargs['until'])
        if kwargs.get('item_id', None):
            _return_data += self._collect_photo_by_id(user, kwargs['item_id'])
        if kwargs.get('albums', None):
            _return_data += self._collect_photo_by_album(user, kwargs['albums'])
        if kwargs.get('friends', None):
            _return_data += self._collect_photo_with_friends(user, kwargs['friends'])
        return _return_data

    def _collect_photo_by_album(self, user, albums):
        """
        :param user:
        :param albums: photo albums array of user
        :return: raw_data of album photos
        TODO: implementation is needed
        """
        _return_data = []
        if 1:
            raise NotImplementedError()
        return _return_data

    def _collect_photo_by_id(self, user, photo_ids):
        """
        :param user:
        :param photo_ids: photo_id's array of user
        :return: raw_data of album photos
        TODO: implementation is needed
        """
        _return_data = []
        if 1:
            raise NotImplementedError()
        return _return_data

    def _collect_photo_with_friends(self, user, friends):
        """
        :param user:
        :param friends: friend list of user to get photos with
        :return: raw_data of album photos
        TODO: implementation is needed
        """
        _return_data = []
        if 1:
            raise NotImplementedError()
        return _return_data

    def _collect_photo_by_date(self, user, since, until):
        access_token = self._get_access_token(user)
        api = facebook.GraphAPI(access_token)
        provider = self.getProvider()
        try:
            result = api.get_connections('me', 'photos', limit=200, since=str(since), until=str(until),
                                         fields='likes.limit(500),comments.limit(500),source,name,sharedposts,images')
        except:
            return None
        _return_data = []
        for obj in result['data']:
            if not RawData.objects.filter(original_id=obj['id']).filter(provider=provider).exists():
                _raw = RawData()
                _raw.owner = user
                _raw.type = RawData.DATA_TYPE['Photo']
                _raw.provider = provider
                try:
                    _raw.original_id = obj['id']
                    _raw.original_path = obj['images'][0]['source']
                    if 'name' in obj:
                        _raw.title = obj['name'][:255]  # first 255 chars of title
                    if 'likes' in obj:
                        _raw.like_count = len(obj['likes']['data'])
                    if 'sharedposts' in obj:
                        _raw.share_count = len(obj['sharedposts']['data'])
                    if 'comments' in obj:
                        _raw.comment_count = len(obj['comments']['data'])
                    _raw.create_date = datetime.datetime.strptime(obj['created_time'], '%Y-%m-%dT%H:%M:%S+0000').replace(tzinfo=pytz.UTC)
                    #TODO error handling (goktan)
                    #_raw.thumbnail = DataManagerUtil.create_photo_thumbnail(settings.SAVE_PREFIX + _raw.data, str(_raw)+ '_thumb'+ _ext_part)
                    Log.debug(_raw)
                    _return_data.append(_raw)
                except Exception as e:
                    Log.error('Could not fetch Facebook photo:' + str(e))
            else:
                _raw = RawData.objects.filter(original_id=obj['id']).get(provider=provider)
                Log.debug(_raw.original_id + ' found in DB')
                _return_data.append(_raw)

        return _return_data

    def collect_status(self, user, **kwargs):
        _return_data = []
        if kwargs['is_date']:
            _return_data += self._collect_status_by_date(user, kwargs['since'], kwargs['until'])
        if kwargs.get('keywords', None):
            _return_data += self._collect_status_by_keywords(user, kwargs['keywords'])
        if kwargs.get('item_id', None):
            _return_data += self._collect_status_by_id(user, kwargs['item_id'])
        if kwargs.get('friends', None):
            _return_data += self._collect_status_with_friends(user, kwargs['friends'])
        return _return_data

    def _collect_status_by_date(self, user, since, until):
        access_token = self._get_access_token(user)
        api = facebook.GraphAPI(access_token)
        provider = self.getProvider()
        try:
            result = api.get_connections('me', 'statuses', limit=200, since=str(since), until=str(until),
                                         fields='id,message,likes.limit(500),comments.limit(500),sharedposts,updated_time')
        except:
            return None
        _return_data = []
        for obj in result['data']:
            if not RawData.objects.filter(original_id=obj['id']).filter(provider=provider).exists():
                try:
                    _statusText = obj['message']
                    if len(_statusText) > 150:
                        Log.debug('Dropping too long user status')
                        continue
                    _raw = RawData()
                    _raw.owner = user
                    _raw.type = RawData.DATA_TYPE['Status']
                    _raw.provider = provider
                    _raw.data = obj['message']
                    if 'likes' in obj:
                        _raw.like_count = len(obj['likes']['data'])
                    if 'sharedposts' in obj:
                        _raw.share_count = len(obj['sharedposts']['data'])
                    if 'comments' in obj:
                        _raw.comment_count = len(obj['comments']['data'])
                    _raw.create_date = datetime.datetime.strptime(obj['updated_time'], '%Y-%m-%dT%H:%M:%S+0000').replace(tzinfo=pytz.UTC)
                    _raw.original_id = obj['id']
                    _return_data.append(_raw)
                except:
                    Log.error('Could not fetch Facebook status')
            else:
                _raw = RawData.objects.filter(original_id=obj['id']).get(provider=provider)
                Log.debug(_raw.original_id + ' found in DB')
                _return_data.append(_raw)
        return _return_data

    def _collect_status_by_id(self, user, status_ids):
        """
        :param user:
        :param status_ids: status_id's array of user
        :return: raw_data of album photos
        TODO: implementation is needed
        """
        _return_data = []
        if 1:
            raise NotImplementedError()
        return _return_data

    def _collect_status_by_keywords(self, user, keywords):
        """
        :param user:
        :param keywords: status_id's array of user
        :return: raw_data of album photos
        TODO: implementation is needed
        """
        _return_data = []
        if 1:
            raise NotImplementedError()
        return _return_data

    def _collect_status_with_friends(self, user, friends):
        """
        :param user:
        :param friends: friend list of user to get photos with
        :return: raw_data of album photos
        TODO: implementation is needed
        """
        _return_data = []
        if 1:
            raise NotImplementedError()
        return _return_data

    def collect_checkin(self, user, **kwargs):
        _return_data = []
        if kwargs['is_date']:
            _return_data += self._collect_checkin_by_date(user, kwargs['since'], kwargs['until'])
        if kwargs.get('friends', None):
            _return_data += self._collect_checkin_with_friends(user, kwargs['friends'])
        return _return_data

    def _collect_checkin_by_date(self, user, since, until):
        access_token = self._get_access_token(user)
        api = facebook.GraphAPI(access_token)
        try:
            result = api.get_connections('me', 'checkins', limit=200, since=str(since), until=str(until),
                                         fields='id,place,likes.limit(500),comments.limit(500),created_time')  # TODO hardcoded limits will go to config file
        except:
            return None

        provider = self.getProvider()

        _return_data = []
        for obj in result['data']:
            if not RawData.objects.filter(original_id=obj['id']).filter(provider=provider).exists():
                _raw = RawData()
                _raw.owner = user
                _raw.type = RawData.DATA_TYPE['Checkin']
                _raw.provider = provider
                try:
                    _raw.data = obj['place']['name']
                    if 'likes' in obj:
                        _raw.like_count = len(obj['likes']['data'])
                    if 'comments' in obj:
                        _raw.comment_count = len(obj['comments']['data'])
                    _raw.create_date = datetime.datetime.strptime(obj['created_time'], '%Y-%m-%dT%H:%M:%S+0000').replace(tzinfo=pytz.UTC)
                    _raw.original_id = obj['id']
                    _return_data.append(_raw)
                except:
                    Log.error('Could not fetch Facebook checkin')
            else:
                _raw = RawData.objects.filter(original_id=obj['id']).get(provider=provider)
                Log.debug(_raw.original_id + ' found in DB')
                _return_data.append(_raw)
        return _return_data

    def _get_access_token(self, user):
        _instance = UserSocialAuth.objects.filter(provider='facebook').get(user=user)
        return _instance.tokens['access_token']

    def _collect_checkin_with_friends(self, user, friends):
        """
        :param user:
        :param friends: friend list of user to get photos with
        :return: raw_data of album photos
        TODO: implementation is needed
        """
        _return_data = []
        if 1:
            raise NotImplementedError()
        return _return_data
