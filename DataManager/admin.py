__author__ = 'ertan'
from django.contrib import admin
from models import *

class MomendAdmin(admin.ModelAdmin):
    list_display = ('owner', 'name', 'thumbnail','create_date')

class MomendScoreAdmin(admin.ModelAdmin):
    list_display = ('momend', 'provider_score')
class RawDataAdmin(admin.ModelAdmin):
    list_display = ('owner', 'type', 'provider', 'original_path', 'thumbnail',
                    'original_id', 'fetch_date', 'data', 'title')

class ProviderAdmin(admin.ModelAdmin):
    pass

class AnimationLayerAdmin(admin.ModelAdmin):
    pass

admin.site.register(Momend, MomendAdmin)
admin.site.register(MomendScore, MomendScoreAdmin)
admin.site.register(RawData, RawDataAdmin)
admin.site.register(Provider, ProviderAdmin)
admin.site.register(AnimationLayer, AnimationLayerAdmin)



