from django.contrib import admin
from models import *

class AnimationGroupAdmin(admin.ModelAdmin):
    pass

class ThemeAdmin(admin.ModelAdmin):
    pass

class ThemeDataAdmin(admin.ModelAdmin):
    pass

class ImageEnhancementAdmin(admin.ModelAdmin):
    pass

class ScenarioAdmin(admin.ModelAdmin):
    pass

admin.site.register(AnimationGroup)
admin.site.register(Theme)
admin.site.register(ThemeData)
admin.site.register(ImageEnhancement)
admin.site.register(Scenario)