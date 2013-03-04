from django.contrib import admin
from models import *


class OutDataAdmin(admin.ModelAdmin):
    list_display = ('raw', 'give_momend_name', 'final_data_path', 'animation', )


class AnimationGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'scenario', 'type', 'duration', 'needed_bg', 'needed_photo', 'needed_status', 'needed_location', 'needed_music']


class ThemeAdmin(admin.ModelAdmin):
    list_display = ['name', ]


class ThemeDataAdmin(admin.ModelAdmin):
    list_display = ['theme', 'type', 'data_path']


class ImageEnhancementAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'script_path', 'parameters', 'example_path']


class EnhancementGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'enhancement_functions', 'post_enhancement', 'applicable_to']


class ScenarioAdmin(admin.ModelAdmin):
    list_display = ['name']


class UserInteractionAnimationGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'stop_current_animation', 'clear_further_animations', 'disable_further_interaction', 'animations']


class CoreAnimationDataAdmin(admin.ModelAdmin):
    list_display = ['group', 'order_in_group', 'used_object_type', 'used_theme_data', 'name', 'type', 'duration',
                    'delay', 'triggerNext', 'waitPrev', 'click_animation', 'hover_animation', 'shadow']
    save_as = True
    list_filter = ('group', 'type', 'used_object_type', 'shadow')
    search_fields = ('group__name', 'used_object_type', 'used_theme_data', 'name')


class DynamicShadowAdmin(admin.ModelAdmin):
    list_display = ['name', 'max_x', 'max_y', 'blur', 'spread', 'color', 'inset']
    save_as = True


class AnimationPlayStatAdmin(admin.ModelAdmin):
    list_display = ['momend', 'date', 'user', 'redirect_url']
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'redirect_url', 'momend__id')
    list_filter = ('date', )


class UserInteractionAdmin(admin.ModelAdmin):
    list_display = ['momend', 'creator', 'date', 'interaction']
    list_filter = ('date', )
    search_fields = ('momend__id', 'momend__owner__username', 'creator__username', 'creator__first_name', 'creator__last_name')


class DeletedUserInteractionAdmin(admin.ModelAdmin):
    list_display = ['momend_id', 'date', 'creator_id', 'momend_owner_deleted', 'delete_time']
    list_filter = ('delete_time', 'momend_owner_deleted')


class PostEnhancementAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name', 'type', 'filepath', 'used_object_type']


class AppliedPostEnhancementAdmin(admin.ModelAdmin):
    list_display = ['type', 'filepath', 'parameters']


admin.site.register(AnimationGroup, AnimationGroupAdmin)
admin.site.register(Theme, ThemeAdmin)
admin.site.register(ThemeData, ThemeDataAdmin)
admin.site.register(ImageEnhancement, ImageEnhancementAdmin)
admin.site.register(EnhancementGroup, EnhancementGroupAdmin)
admin.site.register(Scenario, ScenarioAdmin)
admin.site.register(UserInteractionAnimationGroup, UserInteractionAnimationGroupAdmin)
admin.site.register(CoreAnimationData, CoreAnimationDataAdmin)
admin.site.register(DynamicShadow, DynamicShadowAdmin)
admin.site.register(AnimationPlayStat, AnimationPlayStatAdmin)
admin.site.register(UserInteraction, UserInteractionAdmin)
admin.site.register(DeletedUserInteraction, DeletedUserInteractionAdmin)
admin.site.register(PostEnhancement, PostEnhancementAdmin)
admin.site.register(OutData, OutDataAdmin)
admin.site.register(AppliedPostEnhancement, AppliedPostEnhancementAdmin)
