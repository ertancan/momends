from DataManager.models import BaseDataManagerModel
from django.db import models
from django.forms.models import model_to_dict

class CoreAnimationData(BaseDataManagerModel):
    class Meta:
        verbose_name_plural = 'CoreAnimationData'
        verbose_name = 'CoreAnimationData'
        app_label = 'DataManager'

    USER_DATA_TYPE = [
        '{{USER_PHOTO}}', '{{NEXT_USER_PHOTO}}',
        '{{USER_STATUS}}', '{{NEXT_USER_STATUS}}',
        '{{USER_CHECKIN}}', '{{NEXT_USER_CHECKIN}}',
        '{{USER_BACKGROUND}}', '{{NEXT_USER_BACKGROUND}}',
        '{{USER_MUSIC}}', '{{NEXT_USER_MUSIC}}'
    ]
    group = models.ForeignKey('AnimationGroup')
    used_object_type = models.CharField(max_length=255,null=True,blank=True) #What kind of object? i.e., USER_PHOTO,THEME_BG
    #Consistent with javascript interpreter
    name = models.CharField(max_length=255, null=True, blank=True) #Optional, descriptive, human readable name
    type = models.CharField(max_length=50) #Type of the animation
    duration = models.IntegerField(default=0) #Duration of certain types
    pre = models.TextField(null=True, blank=True) #Precondition of the object to perform the animation
    anim = models.TextField(null=True, blank=True) #Steps to be performed if the type is 'animation'
    target = models.IntegerField(null=True, blank=True) #Animation layer to affect if inter-layer type like wait,block,unblock etc.
    waitPrev = models.BooleanField(default=True) #Whether this animation should wait the previous one to finish or not.
    triggerNext = models.BooleanField(default=True) #Whether this animation should trigger the next one in the queue or not
    force = models.NullBooleanField(null=True, blank=True) #Like force stop now or etc. #TODO serializer should ignore null fields may be?

    click_animation = models.ForeignKey('UserInteractionAnimationGroup', null=True, blank=True, related_name='click_animation')
    hover_animation = models.ForeignKey('UserInteractionAnimationGroup', null=True, blank=True, related_name='hover_animation')

    def __unicode__(self):
        return str(self.group)+'-'+str(self.used_object_type)

    def encode(self):
        enc = model_to_dict(self,exclude=['group','click_animation','hover_animation'])
        if self.click_animation:
            enc['click_animation'] = self.click_animation.encode()
        if self.hover_animation:
            enc['hover_animation'] = self.hover_animation.encode()
        return enc

class ImageEnhancement(BaseDataManagerModel):
    name = models.CharField(max_length=255)

    script_path = models.TextField()
    parameters = models.TextField(null=True, blank=True)
    example_path = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return self.name

class ImageEnhancementGroup(BaseDataManagerModel):
    name = models.CharField(max_length=255)
    image_enhancement_functions = models.CommaSeparatedIntegerField(max_length=255, null=True, blank=True)

    def __unicode__(self):
        return self.name+':'+str(self.image_enhancement_functions)


class Theme(BaseDataManagerModel):
    name = models.CharField(max_length=255)

    image_enhancement_groups = models.ManyToManyField(ImageEnhancementGroup)

    def __unicode__(self):
        return str(self.name)

    def encode(self):
        return self.name

class ThemeData(BaseDataManagerModel):
    class Meta:
        verbose_name_plural = 'ThemeData'
        verbose_name = 'ThemeData'
        app_label = 'DataManager'
    theme = models.ForeignKey(Theme)

    THEME_DATA_TYPE = {
        'Background': 0,
        'Frame': 1,
        'StubPhoto': 2,
        'Font': 3,
        'Music': 4,
        }
    THEME_DATA_TYPE_KEYWORDS = [ #Every data type has 3 keywords, 1st latest data, 2nd next data, 3rd random #!!DO NOT BREAK THE ORDER
                                 '{{THEME_BG}}','{{NEXT_THEME_BG}}','{{RAND_THEME_BG}}', #!!3 is necessary for all types even though you won't use it
                                 '{{THEME_FRAME}}','{{NEXT_THEME_FRAME}}', '{{RAND_THEME_FRAME}}',
                                 '{{THEME_STUB}}','{{NEXT_THEME_STUB}}', '{{RAND_THEME_STUB}}',
                                 '{{THEME_FONT}}','{{NEXT_THEME_FONT}}', '{{RAND_THEME_FONT}}',
                                 '{{THEME_MUSIC}}','{{NEXT_THEME_MUSIC}}', '{{RAND_THEME_MUSIC}}',
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

    def encode(self):
        animations = self.coreanimationdata_set.all()
        resp = []
        for animation in animations:
            resp.append(animation.encode())
        return resp

class UserInteractionAnimationGroup(BaseDataManagerModel):
    name = models.CharField(max_length=255)

    stop_current_animation = models.BooleanField(default=False)
    clear_further_animations = models.BooleanField(default=False)
    disable_further_interaction = models.BooleanField(default=False)

    animations = models.ForeignKey(AnimationGroup)

    def __unicode__(self):
        return self.name

    def encode(self):
        resp = model_to_dict(self,exclude='animations')
        resp['animations'] = self.animations.encode()
        return resp