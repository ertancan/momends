__author__ = 'ertan'
import tweepy
import pytz
from ExternalProviders.BaseProviderWorker import BaseStatusProviderWorker
from models import TwitterProviderModule
from DataManager.models import RawData
from django.conf import settings

class TwitterProviderWorker(BaseStatusProviderWorker):
    def collect_status(self, user, since, until):
        provider = self.getProvider()
        consumer_key = settings.TWITTER_CONSUMER_KEY
        consumer_secret = settings.TWITTER_CONSUMER_SECRET

        access_token,access_token_secret = self._get_access_token_and_secret(user)

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api=tweepy.API(auth)
        _return_data = []
        for i in range(1,16):
            result=api.user_timeline(count=200,page=i)
            if len(result) == 0:
                return _return_data
            for tweet in result:
                if since<tweet.created_at.replace(tzinfo=pytz.UTC)<until:

                    if not RawData.objects.filter(original_id=tweet.id_str).filter(provider=provider).exists():
                        _raw = RawData(share_count=tweet.retweet_count)
                        _raw.owner = user
                        _raw.create_date = tweet.created_at.replace(tzinfo=pytz.UTC)
                        _raw.provider = provider
                        _raw.type = RawData.DATA_TYPE['Status']
                        _raw.original_id = tweet.id_str
                        _raw.data = tweet.text
                        _raw.save()
                        print _raw
                    else:
                        _raw = RawData.objects.filter(original_id=tweet.id_str).get(provider=provider)
                        print _raw.original_id + ' found in DB'
                    _return_data.append(_raw)
                elif tweet.created_at.replace(tzinfo=pytz.UTC)<since:
                    return _return_data
        return _return_data
    def _get_access_token_and_secret(self, user):
        #TODO may need to obtain token
        _obj = TwitterProviderModule.objects.get(owner=user)
        return _obj.token,_obj.user_secret