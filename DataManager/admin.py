__author__ = 'ertan'
from django.contrib import admin
from models import *


class MomendAdmin(admin.ModelAdmin):
    list_display = ('owner', 'name', 'thumbnail', 'create_date', 'cryptic_id')
    list_display_links = ('owner', 'name',)
    list_filter = ('create_date',)
    search_fields = ('owner__username', 'owner__first_name', 'owner__last_name', 'name')


class DeletedMomendAdmin(admin.ModelAdmin):
    list_display = ('owner', 'name', 'thumbnail', 'create_date', 'delete_date', 'play_count')
    list_display_links = ('owner', 'name',)
    list_filter = ('create_date', 'delete_date', 'play_count')
    search_fields = ('owner__username', 'owner__first_name', 'owner__last_name', 'name')


class MomendScoreAdmin(admin.ModelAdmin):
    list_display = ('momend', 'provider_score')


class RawDataAdmin(admin.ModelAdmin):
    list_display = ('owner', 'type', 'provider', 'original_path', 'thumbnail',
                    'original_id', 'fetch_date', 'data', 'title')
    list_filter = ('provider', 'type', 'fetch_date')
    search_fields = ('owner__username', 'owner__first_name', 'owner__last_name', 'title', 'original_id', 'original_path')


class ProviderAdmin(admin.ModelAdmin):
    pass


class AnimationLayerAdmin(admin.ModelAdmin):
    pass

admin.site.register(Momend, MomendAdmin)
admin.site.register(DeletedMomend, DeletedMomendAdmin)
admin.site.register(MomendScore, MomendScoreAdmin)
admin.site.register(RawData, RawDataAdmin)
admin.site.register(Provider, ProviderAdmin)
admin.site.register(AnimationLayer, AnimationLayerAdmin)
