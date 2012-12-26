__author__ = 'ertan'
import tweepy
import pytz
from ExternalProviders.BaseProviderWorker import BaseStatusProviderWorker
from models import TwitterProviderModule
from DataManager.models import RawData
class TwitterProviderWorker(BaseStatusProviderWorker):
    def collect_status(self, user, since, until):
        provider = self.getProvider()
        consumer_key="Od8344pHmAcVr4S2Zq0Nw"    #TODO from environment maybe?
        consumer_secret="NO0b66jiMCroLZNZtAFOi0TzvE7M4pH1vBvCzrCRQ"

        access_token,access_token_secret = self._get_access_token_and_secret(user)

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api=tweepy.API(auth)
        _raw_data = []
        for i in range(1,16):
            result=api.user_timeline(count=200,page=i)
            if len(result) == 0:
                return _raw_data
            for tweet in result:
                if since<tweet.created_at<until:
                    _raw = RawData(share_count=tweet.retweet_count)
                    _raw.create_date = tweet.created_at.replace(tzinfo=pytz.UTC)
                    _raw.source = provider
                    _raw.type = RawData.DATA_TYPE['Status']
                    _raw.original_id = tweet.id_str
                    _raw.data = tweet.text
                    _raw_data.append(_raw);
                elif tweet.created_at<since:
                    return _raw_data
        return _raw_data
    def _get_access_token_and_secret(self, user):
        #TODO may need to obtain token
        _obj = TwitterProviderModule.objects.get(owner=user)
        return _obj.token,_obj.user_secret