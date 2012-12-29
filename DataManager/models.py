from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
# Create your models here.
class BaseDataManagerModel(models.Model):
    class Meta:
        abstract = True
        app_label = 'DataManager'

class Momend(BaseDataManagerModel):
    owner = models.ForeignKey(User)
    create_date = models.DateTimeField(auto_now_add=True)

    momend_start_date = models.DateTimeField()
    momend_end_date = models.DateTimeField()

    #TODO stats

    def __unicode__(self):
        return str(self.owner) + ':'+str(self.momend_start_date)+' - '+str(self.momend_end_date)

    def encode(self):
        enc = model_to_dict(self)
        layers = []
        for layer in AnimationLayer.objects.filter(momend=self):
            layers.append(layer.encode())
        enc['animation_layers'] = layers
        return enc

class AnimationLayer(BaseDataManagerModel):
    momend = models.ForeignKey(Momend)
    layer = models.IntegerField() #Like layer0, layer1 etc.
    description = models.CharField(max_length=255)

    class Meta:
        unique_together = ('momend', 'layer')

    def __unicode__(self):
        return str(self.momend)+' : '+str(self.layer)+'-'+str(self.description)

    def encode(self):
        enc = []
        for out in OutData.objects.filter(owner_layer=self):
            enc.append(out.encode())
        return enc

class Provider(BaseDataManagerModel):
    name = models.CharField(max_length = 50)
    package_name = models.CharField(max_length = 255)
    module_name = models.CharField(max_length = 255)
    worker_name = models.CharField(max_length = 255)

    def __unicode__(self):
        return str(self.name)

class RawData(BaseDataManagerModel):
    class Meta:
        verbose_name_plural = 'RawData'
        verbose_name = 'RawData'
    owner = models.ForeignKey(User)

    original_path = models.CharField(max_length=500) #original path of data if it exists
    original_id = models.CharField(max_length=255) #original id of data represents the source id
    data = models.TextField() #main data to use in momend
    title = models.CharField(max_length=255)

    DATA_TYPE= {'Photo': 0,
                'Status': 1,
                'Checkin': 2}
    type = models.IntegerField(choices=[[DATA_TYPE[key],key] for key in DATA_TYPE.keys()])

    provider = models.ForeignKey(Provider)


    create_date = models.DateTimeField(default = datetime.now)
    fetch_date = models.DateTimeField(auto_now_add = True)

    like_count = models.IntegerField(default = 0)
    comment_count = models.IntegerField(default = 0)
    share_count = models.IntegerField(default = 0)

    #TODO latitude,longitude etc.

    def __unicode__(self):
        return str(self.owner)+'_'+str(self.provider)+'_'+str(self.original_id)

class CoreAnimationData(BaseDataManagerModel):
    class Meta:
        verbose_name_plural = 'CoreAnimationData'
        verbose_name = 'CoreAnimationData'
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

    def __unicode__(self):
        return str(self.group)+'-'+str(self.used_object_type)

    def encode(self):
        enc = model_to_dict(self,exclude=['group'])
        return enc

class OutData(BaseDataManagerModel):
    class Meta:
        verbose_name_plural = 'OutData'
        verbose_name = 'OutData'
    owner_layer = models.ForeignKey(AnimationLayer)
    raw = models.ForeignKey(RawData,null=True, blank=True) #If created by enriching or enhancing a raw data

    #Enriched Data
    priority = models.IntegerField(default=0)
    selection_criteria = models.TextField(null=True, blank=True) #TODO foreign key may be

    #Enhanced Data
    theme = models.ForeignKey('Theme', null=True, blank=True)

    #Keeps the latest path or reference to the object
    final_data_path = models.TextField(null=True, blank=True)

    #Animation Data
    animation = models.ForeignKey(CoreAnimationData, null=True, blank= True)

    def __unicode__(self):
        return str(self.owner_layer)+':'+str(self.theme)+'='+str(self.animation)

    def encode(self):
        enc = model_to_dict(self,fields=['priority','selection_criteria','final_data_path'])
        enc['theme'] = self.theme.encode()
        enc['animation'] = self.animation.encode()
        return enc







