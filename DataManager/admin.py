__author__ = 'ertan'
from django.contrib import admin
from models import *
from ExternalProviders.FacebookProvider.models import FacebookProviderModule
from ExternalProviders.TwitterProvider.models import TwitterProviderModule

admin.site.register(Momend)
admin.site.register(RawData)
admin.site.register(AnimationLayer)
admin.site.register(AnimationGroup)
admin.site.register(Theme)
admin.site.register(ThemeData)
admin.site.register(Scenario)
admin.site.register(CoreAnimationData)
admin.site.register(Provider)
admin.site.register(OutData)

admin.site.register(FacebookProviderModule)
admin.site.register(TwitterProviderModule)
