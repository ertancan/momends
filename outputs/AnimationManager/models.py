from DataManager.models import BaseDataManagerModel
from django.db import models

class ImageEnhancement(BaseDataManagerModel):
    name = models.CharField(max_length=255)

    script_path = models.TextField()
    parameters = models.TextField(null=True, blank=True)
    example_path = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return self.name

class Theme(BaseDataManagerModel):
    name = models.CharField(max_length=255)

    image_enhancement_functions = models.CommaSeparatedIntegerField(max_length=255, null=True, blank=True)

    def __unicode__(self):
        return str(self.name)

    def encode(self):
        return self.name

class ThemeData(BaseDataManagerModel):
    theme = models.ForeignKey(Theme)

    THEME_DATA_TYPE = {
        'Background': 0,
        'Frame': 1,
        'StubPhoto': 2,
        'Font': 3,
        'Music': 4,
        }
    THEME_DATA_TYPE_KEYWORDS = [ #Every data type has 2 keywords, 1st latest data, 2nd next data #!!DO NOT BREAK THE ORDER
                                 '{{THEME_BG}}','{{NEXT_THEME_BG}}', #!!2 is necessary for all types even though you won't use it
                                 '{{THEME_FRAME}}','{{NEXT_THEME_FRAME}}',
                                 '{{THEME_STUB}}','{{NEXT_THEME_STUB}}',
                                 '{{THEME_FONT}}','{{NEXT_THEME_FONT}}',
                                 '{{THEME_MUSIC}}','{{NEXT_THEME_MUSIC}}',
                                 ]
    type = models.IntegerField(choices=[[THEME_DATA_TYPE[key],key] for key in THEME_DATA_TYPE.keys()])
    data_path = models.CharField(max_length=255)

    #TODO Different resolutions may be?

    def __unicode__(self):
        return str(self.theme)+':'+str(self.type)+'='+str(self.data_path)

class Scenario(BaseDataManagerModel):
    name = models.CharField(max_length=255)

    compatible_themes = models.ManyToManyField(Theme)

    def __unicode__(self):
        return str(self.name)

class AnimationGroup(BaseDataManagerModel):
    name = models.CharField(max_length=255)

    scenario = models.ForeignKey(Scenario)

    duration = models.IntegerField()

    ANIMATION_GROUP_TYPE = {
        'Background': 0,
        'Music': 1,
        'SceneChange': 2,
        'Normal': 3,
        }
    type = models.IntegerField(choices=[[ANIMATION_GROUP_TYPE[key],key] for key in ANIMATION_GROUP_TYPE.keys()])

    needed_bg = models.IntegerField('Needed user background', default=0)
    needed_music = models.IntegerField('Needed user music', default=0)
    needed_photo = models.IntegerField('Needed user photo', default=0)
    needed_status = models.IntegerField('Needed user status', default=0)
    needed_location = models.IntegerField('Needed user location', default=0)

    def __unicode__(self):
        return str(self.name)+':'+str(self.scenario)+'='+str(self.duration)
