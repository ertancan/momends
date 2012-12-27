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
    original_id = models.CharField(max_length=255) #original id of data represents the source id
    data = models.TextField() #main data to use in momend

    DATA_TYPE= {'Photo': 0,
                'Status': 1,
                'Checkin': 2}
    type = models.IntegerField(choices=[[DATA_TYPE[key],key] for key in DATA_TYPE.keys()])

    source = models.ForeignKey(Provider)

    create_date = models.DateTimeField(default = datetime.now)
    fetch_date = models.DateTimeField(auto_now_add = True)

    like_count = models.IntegerField(default = 0)
    comment_count = models.IntegerField(default = 0)
    share_count = models.IntegerField(default = 0)

    #TODO latitude,longitude etc.

class CoreAnimationData(BaseDataManagerModel):
    group = models.ForeignKey('AnimationGroup')
    used_object_type = models.CharField(max_length=255)
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

class OutData(BaseDataManagerModel):
    owner_layer = models.ForeignKey(AnimationLayer)
    raw = models.ForeignKey(RawData,null=True, blank=True) #If created by enriching or enhancing a raw data

    #Enriched Data
    priority = models.IntegerField(default=0)
    selection_criteria = models.TextField(null=True, blank=True) #TODO foreign key may be

    #Enhanced Data
    theme = models.ForeignKey('Theme', null=True, blank=True)

    #Keeps the latest path or reference to the object
    out_data = models.TextField(null=True, blank=True)

    #Animation Data
    animation = models.ForeignKey(CoreAnimationData, null=True, blank= True)

class Theme(BaseDataManagerModel):
    name = models.CharField(max_length=255)

    image_enhancement_function = models.CharField(max_length=255) #TODO External model to keep parameters etc.

class ThemeData(BaseDataManagerModel):
    theme = models.ForeignKey(Theme)

    THEME_DATA_TYPE = {
        'Background': 0,
        'Frame': 1,
        'StubPhoto': 2,
        'Font': 3,
        'Music': 4,
    }
    type = models.IntegerField(choices=[[THEME_DATA_TYPE[key],key] for key in THEME_DATA_TYPE.keys()])
    data_path = models.CharField(max_length=255)

    #TODO Different resolutions may be?

class Scenario(BaseDataManagerModel):
    name = models.CharField(max_length=255)

    compatible_themes = models.ManyToManyField(Theme)

class AnimationGroup(BaseDataManagerModel):
    name = models.CharField(max_length=255)

    scenario = models.ForeignKey(Scenario)

    duration = models.IntegerField()

    ANIMATION_GROUP_TYPE = {
        'Background': 0,
        'Music': 0,
        'SceneChange': 0,
        'Normal': 0,
    }
    type = models.IntegerField(choices=[[ANIMATION_GROUP_TYPE[key],key] for key in ANIMATION_GROUP_TYPE.keys()])

    needed_bg = models.IntegerField(default=0)
    needed_music = models.IntegerField(default=0)
    needed_photo = models.IntegerField(default=0)
    needed_status = models.IntegerField(default=0)
    needed_location = models.IntegerField(default=0)








