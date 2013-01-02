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

class ImageEnhancementGroupAdmin(admin.ModelAdmin):
    pass

class ScenarioAdmin(admin.ModelAdmin):
    pass

admin.site.register(AnimationGroup,AnimationGroupAdmin)
admin.site.register(Theme,ThemeAdmin)
admin.site.register(ThemeData,ThemeDataAdmin)
admin.site.register(ImageEnhancement,ImageEnhancementAdmin)
admin.site.register(ImageEnhancementGroup,ImageEnhancementGroupAdmin)
admin.site.register(Scenario,ScenarioAdmin)