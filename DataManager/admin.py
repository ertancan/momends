__author__ = 'ertan'
from django.contrib import admin
from models import *
from DataManagerUtil import DataManagerUtil
from django.contrib import messages


class MomendAdmin(admin.ModelAdmin):
    def send_mail_to_owners(self, request, queryset):
        for momend in queryset:
            _successful = DataManagerUtil.send_momend_created_email(momend)
            if _successful:
                messages.success(request, 'Successful: '+str(momend.id))
            else:
                messages.error(request, 'Error: '+str(momend.id))
    send_mail_to_owners.short_description = 'Send links to owners'

    list_display = ('owner', 'name', 'thumbnail', 'create_date', 'cryptic_id')
    list_display_links = ('owner', 'name',)
    list_filter = ('create_date',)
    search_fields = ('owner__username', 'owner__first_name', 'owner__last_name', 'name')
    actions = [send_mail_to_owners]


class MomendStatusAdmin(admin.ModelAdmin):
    list_display = ('momend', 'status', 'message', 'last_update')
    list_filter = ('status',)
    search_fields = ('momend__owner__username', 'momend__cryptic_id', 'momend__pk', 'message')


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
admin.site.register(MomendStatus, MomendStatusAdmin)
admin.site.register(DeletedMomend, DeletedMomendAdmin)
admin.site.register(MomendScore, MomendScoreAdmin)
admin.site.register(RawData, RawDataAdmin)
admin.site.register(Provider, ProviderAdmin)
admin.site.register(AnimationLayer, AnimationLayerAdmin)
