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
        if kwargs.get('albums', None):
            _return_data += self._collect_photo_by_album(user, kwargs['albums'])
        if kwargs.get('item_id', None):
            _return_data += self._collect_photo_by_id(user, kwargs['item_id'])
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

    def _collect_photo_by_date(self, user, since, until):
        access_token = self._get_access_token(user)
        api = facebook.GraphAPI(access_token)
        provider = self.getProvider()
        try:
            result = api.get_connections('me', 'photos', limit=200, since=str(since), until=str(until),
                                         fields='likes.limit(500),comments.limit(500),source,name,sharedposts,images,tags')
        except:
            Log.error('Exception on collect Photo')
            return None
        _return_data = []
        Log.info('Found ' + str(len(result['data'])) + ' Photos')
        for obj in result['data']:
            try:
                _raw, _is_new = RawData.objects.get_or_create(original_id=obj['id'], provider=provider,
                                                              defaults={'owner': user, 'type': RawData.DATA_TYPE['Photo'],
                                                                        'original_path': obj['images'][0]['source']})
                if _is_new:
                    if 'name' in obj:
                        _raw.title = obj['name'][:255]  # first 255 chars of title
                    _raw.create_date = datetime.datetime.strptime(obj['created_time'], '%Y-%m-%dT%H:%M:%S+0000').replace(tzinfo=pytz.UTC)
                if 'likes' in obj:
                    _raw.like_count = len(obj['likes']['data'])
                if 'sharedposts' in obj:
                    _raw.share_count = len(obj['sharedposts']['data'])
                if 'comments' in obj:
                    _raw.comment_count = len(obj['comments']['data'])
                _raw.tags = FacebookProviderWorker._get_tags(obj)
                _raw.save()
                Log.debug('Fetched Facebook Photo: ' + str(_raw))
                _return_data.append(_raw)
            except Exception as e:
                Log.error('Could not fetch Facebook Photo:' + str(e))
        return _return_data

    def collect_status(self, user, **kwargs):
        _return_data = []
        if kwargs['is_date']:
            _return_data += self._collect_status_by_date(user, kwargs['since'], kwargs['until'])
        if kwargs.get('keywords', None):
            _return_data += self._collect_status_by_keywords(user, kwargs['keywords'])
        if kwargs.get('item_id', None):
            _return_data += self._collect_status_by_id(user, kwargs['item_id'])
        return _return_data

    def _collect_status_by_date(self, user, since, until):
        access_token = self._get_access_token(user)
        api = facebook.GraphAPI(access_token)
        provider = self.getProvider()
        try:
            result = api.get_connections('me', 'statuses', limit=200, since=str(since), until=str(until),
                                         fields='id,message,likes.limit(500),comments.limit(500),sharedposts,updated_time,tags')
        except:
            Log.error('Exception on collect Status')
            return None
        _return_data = []
        Log.info('Found ' + str(len(result['data'])) + ' Statuses')
        for obj in result['data']:
            try:
                _raw, _is_new = RawData.objects.get_or_create(original_id=obj['id'], provider=provider,
                                                              defaults={'owner': user, 'type': RawData.DATA_TYPE['Status'],
                                                                        'data': obj['message']})
                if _is_new:
                    if len(_raw.data) > 150:
                        Log.debug('Dropping too long user status')
                        _raw.delete()
                        continue
                    _raw.create_date = datetime.datetime.strptime(obj['updated_time'], '%Y-%m-%dT%H:%M:%S+0000').replace(tzinfo=pytz.UTC)
                if 'likes' in obj:
                    _raw.like_count = len(obj['likes']['data'])
                if 'sharedposts' in obj:
                    _raw.share_count = len(obj['sharedposts']['data'])
                if 'comments' in obj:
                    _raw.comment_count = len(obj['comments']['data'])
                _raw.tags = FacebookProviderWorker._get_tags(obj)
                _raw.save()
                Log.debug('Fetched Facebook Status: ' + str(_raw))
                _return_data.append(_raw)
            except Exception as e:
                Log.error('Could not fetch Facebook status: ' + str(e))
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

    def collect_checkin(self, user, **kwargs):
        _return_data = []
        if kwargs['is_date']:
            _return_data += self._collect_checkin_by_date(user, kwargs['since'], kwargs['until'])
        return _return_data

    def _collect_checkin_by_date(self, user, since, until):
        access_token = self._get_access_token(user)
        api = facebook.GraphAPI(access_token)
        try:
            result = api.get_connections('me', 'checkins', limit=200, since=str(since), until=str(until),
                                         fields='id,place,likes.limit(500),comments.limit(500),created_time,tags')  # TODO hardcoded limits will go to config file
        except:
            Log.error('Exception on collect Checkin')
            return None

        provider = self.getProvider()

        _return_data = []

        Log.info('Found ' + str(len(result['data'])) + ' Checkins')
        for obj in result['data']:
            try:
                _raw, _is_new = RawData.objects.get_or_create(original_id=obj['id'], provider=provider,
                                                              defaults={'owner': user, 'type': RawData.DATA_TYPE['Checkin'],
                                                                        'data': obj['place']['name']})
                if _is_new:
                    _raw.create_date = datetime.datetime.strptime(obj['created_time'], '%Y-%m-%dT%H:%M:%S+0000').replace(tzinfo=pytz.UTC)
                if 'likes' in obj:
                    _raw.like_count = len(obj['likes']['data'])
                if 'comments' in obj:
                    _raw.comment_count = len(obj['comments']['data'])
                _raw.tags = FacebookProviderWorker._get_tags(obj)
                _raw.save()
                Log.debug('Fetched Facebook Checkin: ' + str(_raw))
                _return_data.append(_raw)
            except Exception as e:
                Log.error('Could not fetch Facebook checkin:' + str(e))
        return _return_data

    def get_friendlist(self, user):
        access_token = self._get_access_token(user)
        api = facebook.GraphAPI(access_token)
        return api.get_connections("me", "friends")['data']

    def get_friend_name_from_id(self, user, friend_id):
        access_token = self._get_access_token(user)
        api = facebook.GraphAPI(access_token)
        _result = api.get_object(friend_id)
        return _result['first_name']

    def _get_access_token(self, user):
        _instance = UserSocialAuth.objects.filter(provider='facebook').get(user=user)
        return _instance.tokens['access_token']

    @staticmethod
    def _get_tags(obj):
        """
            Returns comma seperated list of ids who likes the given object
        """
        if 'tags' in obj:
            _tag_str = ''
            for _tag in obj['tags']['data']:
                if 'id' in _tag:
                    _tag_str += _tag['id'] + ','
            return _tag_str
        return None
