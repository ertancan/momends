__author__ = 'ertan'
import tweepy
import pytz
from ExternalProviders.BaseProviderWorker import BaseStatusProviderWorker
from DataManager.models import RawData
from django.conf import settings
from social_auth.db.django_models import UserSocialAuth
from LogManagers.Log import Log


class TwitterProviderWorker(BaseStatusProviderWorker):

    def collect_status(self, user, **kwargs):
        _return_data = []
        if kwargs['is_date']:
            _return_data += self._collect_status_by_date(user, kwargs['since'], kwargs['until'])
        if kwargs.get('keywords', None):
            _return_data += self._collect_status_by_keywords(user, kwargs['keywords'])
        if kwargs.get('item_id', None):
            _return_data += self._collect_status_by_id(user, kwargs['item_id'])
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

    def _collect_status_by_date(self, user, since, until):
        provider = self.getProvider()
        consumer_key = settings.TWITTER_CONSUMER_KEY
        consumer_secret = settings.TWITTER_CONSUMER_SECRET

        access_token, access_token_secret = self._get_access_token_and_secret(user)

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)
        _return_data = []
        for i in range(1, 16):
            try:
                result = api.user_timeline(count=200, page=i)
            except Exception:
                Log.error('Twitter data collect error')
                return _return_data

            if len(result) == 0:
                return _return_data

            for tweet in result:
                if since < tweet.created_at.replace(tzinfo=pytz.UTC) < until:
                    _raw, _is_new = RawData.objects.get_or_create(original_id=tweet.id_str, provider=provider,
                                                                  defaults={'owner': user, 'type': RawData.DATA_TYPE['Status'],
                                                                            'data': tweet.text})
                    if _is_new:
                        _raw.create_date = tweet.created_at.replace(tzinfo=pytz.UTC)
                        _raw.original_path = 'twitter.com/' + user.social_auth.get(provider='twitter').uid + '/status/' + tweet.id_str
                        _raw.tags = tweet.in_reply_to_user_id_str
                        Log.debug(_raw)
                    _raw.share_count = tweet.retweet_count
                    _raw.save()
                    Log.debug('Fetched Twitter Status: ' + str(_raw))
                    _return_data.append(_raw)
                elif tweet.created_at.replace(tzinfo=pytz.UTC) < since:
                    return _return_data
        return _return_data

    def get_friendlist(self, user):
        _consumer_key = settings.TWITTER_CONSUMER_KEY
        _consumer_secret = settings.TWITTER_CONSUMER_SECRET
        _access_token, _access_token_secret = self._get_access_token_and_secret(user)
        _auth = tweepy.OAuthHandler(_consumer_key, _consumer_secret)
        _auth.set_access_token(_access_token, _access_token_secret)
        _api = tweepy.API(_auth)

        _result = []

        for _page in tweepy.Cursor(_api.friends).pages():
            for _friend in _page:
                _result.append({'id': _friend.id_str, 'name': _friend.name, 'screen_name': _friend.screen_name})
        return _result

    def _get_access_token_and_secret(self, user):
        UserSocialAuth.objects.filter()
        _instance = UserSocialAuth.objects.filter(provider='twitter').get(user=user)
        return _instance.tokens['oauth_token'], _instance.tokens['oauth_token_secret']
