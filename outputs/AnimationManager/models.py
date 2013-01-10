from DataManager.models import BaseDataManagerModel
from django.db import models
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from DataManager.models import RawData,Momend
from django.utils import simplejson
from datetime import datetime

class OutData(BaseDataManagerModel):
    class Meta:
        verbose_name_plural = 'OutData'
        verbose_name = 'OutData'
        app_label = 'DataManager'
    owner_layer = models.ForeignKey('AnimationLayer')
    raw = models.ForeignKey(RawData,null=True, blank=True) #If created by enriching or enhancing a raw data

    #Enriched Data
    priority = models.IntegerField(default=0)
    selection_criteria = models.TextField(null=True, blank=True) #TODO foreign key may be

    #Enhanced Data
    theme = models.ForeignKey('Theme', null=True, blank=True)

    #Keeps the latest path or reference to the object
    final_data_path = models.TextField(null=True, blank=True)
    parameters = models.TextField(null=True, blank=True)

    #Animation Data
    animation = models.ForeignKey('CoreAnimationData', null=True, blank= True)

    def __unicode__(self):
        return str(self.owner_layer)+':'+str(self.theme)+'='+str(self.animation)

    def encode(self):
        enc = model_to_dict(self,fields=['priority','selection_criteria','final_data_path','parameters'])
        enc['theme'] = self.theme.encode()
        enc['animation'] = self.animation.encode()
        if self.raw and (self.raw.type == RawData.DATA_TYPE['Status']):
            enc['data'] = self.raw.data
        post_enhancements = self.appliedpostenhancement_set
        if post_enhancements.count() > 0:
            posts = []
            for enh in post_enhancements.all():
                posts.append(enh.encode())

            enc['post_enhancements'] = posts

        return enc

    def give_momend_name(self):
        return self.owner_layer.momend
    give_momend_name.short_description = 'Momend'


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
    used_object_type = models.CharField(max_length=255, null=True, blank=True) #What kind of object? i.e., USER_PHOTO,THEME_BG
    used_object_id = models.CharField('Id of the object, if known' ,max_length=255, null=True, blank=True)
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
        enc = model_to_dict(self,exclude=['group','click_animation','hover_animation','used_object_id'])
        if self.click_animation:
            enc['click_animation'] = self.click_animation.encode()
        if self.hover_animation:
            enc['hover_animation'] = self.hover_animation.encode()
        if self.used_object_id:
            enc['object'] = self.used_object_id
        return enc

class ImageEnhancement(BaseDataManagerModel):
    name = models.CharField(max_length=255)

    script_path = models.TextField()
    parameters = models.TextField(null=True, blank=True)
    example_path = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return self.name

class PostEnhancement(BaseDataManagerModel):
    name = models.CharField(max_length=255)
    filepath = models.CharField(max_length=500, null= True, blank= True)
    used_object_type = models.CharField(max_length=255, null=True, blank=True) #What kind of object? i.e., USER_PHOTO,THEME_BG
    parameters = models.CharField(max_length=255, null=True, blank=True)

    type = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name+':'+str(self.type)

class AppliedPostEnhancement(BaseDataManagerModel):
    outdata = models.ForeignKey(OutData)

    filepath = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    parameters = models.CharField(max_length=255) #This parameters overrides ThemeData parameters!

    def __unicode__(self):
        return str(self.type)+':'+self.filepath

    def encode(self):
        return model_to_dict(self,exclude='outdata')


class EnhancementGroup(BaseDataManagerModel):
    name = models.CharField(max_length=255)
    enhancement_functions = models.CommaSeparatedIntegerField(max_length=255, null=True, blank=True)

    post_enhancement = models.BooleanField(default = False)
    applicable_to = models.IntegerField(choices=[[RawData.DATA_TYPE[key],key] for key in RawData.DATA_TYPE.keys()])

    def __unicode__(self):
        return self.name+':'+str(self.enhancement_functions)


class Theme(BaseDataManagerModel):
    name = models.CharField(max_length=255)

    enhancement_groups = models.ManyToManyField(EnhancementGroup)

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
    parameters = models.TextField(null=True, blank=True)

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

    scenario = models.ForeignKey(Scenario, null=True)

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

class AnimationPlayStat(BaseDataManagerModel):
    momend = models.ForeignKey('Momend')
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, null=True, blank=True)
    redirect_url = models.CharField(max_length=500)

    def __unicode__(self):
        return str(self.momend) + ':'+ str(self.user)+'='+str(self.date)

class UserInteraction(BaseDataManagerModel):
    momend = models.ForeignKey('Momend')
    date = models.DateTimeField(auto_now_add=True)
    interaction = models.TextField()

    def __unicode__(self):
        return str(self.momend)+':'+str(self.date)+'='+str(self.interaction)

    def encode(self):
        momend_data = self.momend.encode()
        momend_data['animation_layers'].append(simplejson.loads(self.interaction))
        momend_data['interaction_date'] = self.date
        return momend_data

    def toJSON(self):
        return simplejson.dumps(self.encode(), default=lambda obj: obj.isoformat() if isinstance(obj, datetime) else None)

