__author__ = 'ertan'
import tweepy
from ExternalProviders.BaseProviderWorker import BaseStatusProviderWorker
from models import TwitterProviderModule
class TwitterProviderWorker(BaseStatusProviderWorker):
    def collect_status(self,user,since,until):
        consumer_key="Od8344pHmAcVr4S2Zq0Nw"    #TODO from environment maybe?
        consumer_secret="NO0b66jiMCroLZNZtAFOi0TzvE7M4pH1vBvCzrCRQ"

        access_token,access_token_secret = self._get_access_token_and_secret(user)

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api=tweepy.API(auth)

        for i in range(1,16):
            result=api.user_timeline(count=200,page=i)
            if len(result) == 0:
                return
            for tweet in result:
                if since<tweet.created_at<until:
                    print(str(tweet.created_at)+':'+tweet.text+':'+str(tweet.retweet_count))
                elif tweet.created_at<since:
                    return

    def _get_access_token_and_secret(self,user):
        #TODO may need to obtain token
        _obj = TwitterProviderModule.objects.get(owner=user)
        return _obj.token,_obj.user_secret