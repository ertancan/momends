__author__ = 'ertan'
from django.contrib import admin
from models import *

class MomendAdmin(admin.ModelAdmin):
    list_display = ('owner', 'name', 'create_date',)


class RawDataAdmin(admin.ModelAdmin):
    list_display = ('owner', 'type', 'provider', 'original_path',
                    'original_id', 'fetch_date', 'data', 'title')


class AnimationLayerAdmin(admin.ModelAdmin):
    pass

class ProviderAdmin(admin.ModelAdmin):
    pass

class OutDataAdmin(admin.ModelAdmin):
    list_display = ('raw', 'give_momend_name', 'final_data_path', 'animation', )

admin.site.register(Momend, MomendAdmin)
admin.site.register(RawData, RawDataAdmin)
admin.site.register(AnimationLayer, AnimationLayerAdmin)
admin.site.register(Provider, ProviderAdmin)
admin.site.register(OutData, OutDataAdmin)



