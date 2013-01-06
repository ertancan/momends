from django.contrib import admin
from models import *

class AnimationGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'scenario', 'type', 'duration', 'needed_bg', 'needed_photo', 'needed_status', 'needed_location', 'needed_music']

class ThemeAdmin(admin.ModelAdmin):
    list_display = ['name'  ]

class ThemeDataAdmin(admin.ModelAdmin):
    list_display = ['theme', 'type', 'data_path']

class ImageEnhancementAdmin(admin.ModelAdmin):
    list_display = ['name', 'script_path', 'parameters', 'example_path']

class ImageEnhancementGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'image_enhancement_functions']

class ScenarioAdmin(admin.ModelAdmin):
    list_display = ['name']

class UserInteractionAnimationGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'stop_current_animation', 'clear_further_animations', 'disable_further_interaction', 'animations']

class CoreAnimationDataAdmin(admin.ModelAdmin):
    list_display = ['group', 'used_object_type', 'name', 'type', 'duration', 'click_animation', 'hover_animation']

class AnimationPlayStatAdmin(admin.ModelAdmin):
    list_display = ['momend', 'date', 'user', 'redirect_url']

class UserInteractionAdmin(admin.ModelAdmin):
    list_display = ['momend','date','interaction']

admin.site.register(AnimationGroup, AnimationGroupAdmin)
admin.site.register(Theme, ThemeAdmin)
admin.site.register(ThemeData, ThemeDataAdmin)
admin.site.register(ImageEnhancement, ImageEnhancementAdmin)
admin.site.register(ImageEnhancementGroup, ImageEnhancementGroupAdmin)
admin.site.register(Scenario, ScenarioAdmin)
admin.site.register(UserInteractionAnimationGroup, UserInteractionAnimationGroupAdmin)
admin.site.register(CoreAnimationData, CoreAnimationDataAdmin)
admin.site.register(AnimationPlayStat, AnimationPlayStatAdmin)
admin.site.register(UserInteraction, UserInteractionAdmin)
