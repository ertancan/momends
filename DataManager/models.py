from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
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

class AnimationLayer(BaseDataManagerModel):
    momend = models.ForeignKey(Momend)
    layer = models.IntegerField() #Like layer0, layer1 etc.
    description = models.CharField(max_length=255)

    class Meta:
        unique_together = ('momend', 'layer')

class Provider(BaseDataManagerModel):
    name = models.CharField(max_length = 50)
    package_name = models.CharField(max_length = 255)
    module_name = models.CharField(max_length = 255)
    worker_name = models.CharField(max_length = 255)

class RawData(BaseDataManagerModel):
    original_path = models.CharField(max_length=500) #original path of data if it exists
    original_id = models.TextField() #original id of data represents the source id #TODO check here if char is needed?
    data = models.TextField() #main data to use in momend

    DATA_TYPE= {'Photo': 0,'Status': 1,'Checkin': 2} #TODO less ugly may be?
    _data_choices = (
        (0, 'Photo'),
        (1, 'Status'),
        (2, 'Checkin'),
        )
    type = models.IntegerField(choices = _data_choices)

    source = models.ForeignKey(Provider)

    create_date = models.DateTimeField(default = datetime.now)
    fetch_date = models.DateTimeField(auto_now_add = True)

    like_count = models.IntegerField(default = 0)
    comment_count = models.IntegerField(default = 0)
    share_count = models.IntegerField(default = 0)

    #TODO latitude,longitude etc.

class OutData(BaseDataManagerModel):
    owner_layer = models.ForeignKey(AnimationLayer)
    raw = models.ForeignKey(RawData,null=True,blank=True) #If created by enriching or enhancing a raw data

    #Enriched Data
    priority = models.IntegerField(default=0)
    selection_criteria = models.TextField() #TODO foreign key may be

    #Enhanced Data
    theme_id = models.IntegerField(default=0) #TODO foreign key to theme table
    enhanced_data_path = models.TextField()

    #Animation Data (parts after underscore is consistent with javascript interpreter)
    animation_name = models.CharField(max_length=255,null=True,blank=True) #Optional, descriptive, human readable name if
    animation_type = models.CharField(max_length=50) #Type of the animation
    animation_duration = models.IntegerField(default=0) #Duration of certain types
    animation_pre = models.TextField(null=True,blank=True) #Precondition of the object to perform the animation
    animation_anim = models.TextField(null=True,blank=True) #Steps to be performed if the type is 'animation'
    animation_target = models.IntegerField(null=True,blank=True) #Animation layer to affect if inter-layer type like wait,block,unblock etc.
    animation_waitPrev = models.BooleanField(default=True) #Whether this animation should wait the previous one to finish or not.
    animation_triggerNext = models.BooleanField(default=True) #Whether this animation should trigger the next one in the queue or not
    animation_force = models.BooleanField(null=True,blank=True) #Like force stop now or etc. #TODO serializer should ignore null fields may be?







