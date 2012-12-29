__author__ = 'ertan'
from django.contrib import admin
from models import *
from ExternalProviders.FacebookProvider.models import FacebookProviderModule
from ExternalProviders.TwitterProvider.models import TwitterProviderModule

class MomendAdmin(admin.ModelAdmin):
    list_display = ('owner', 'create_date')
    pass

class RawDataAdmin(admin.ModelAdmin):
    list_display = ('owner', 'type', 'provider', 'original_path',
                    'original_id', 'fetch_date', 'data', 'title')
    pass

class AnimationLayerAdmin(admin.ModelAdmin):
    pass

class CoreAnimationDataAdmin(admin.ModelAdmin):
    pass

class ProviderAdmin(admin.ModelAdmin):
    pass

class OutDataAdmin(admin.ModelAdmin):
    pass

class FacebookProviderModuleAdmin(admin.ModelAdmin):
    pass

class TwitterProviderModuleAdmin(admin.ModelAdmin):
    pass

admin.site.register(Momend, MomendAdmin)
admin.site.register(RawData, RawDataAdmin)
admin.site.register(AnimationLayer, AnimationLayerAdmin)
admin.site.register(CoreAnimationData, CoreAnimationDataAdmin)
admin.site.register(Provider, ProviderAdmin)
admin.site.register(OutData, OutDataAdmin)

admin.site.register(FacebookProviderModule, FacebookProviderModuleAdmin)
admin.site.register(TwitterProviderModule, TwitterProviderModuleAdmin)

