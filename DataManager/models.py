from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from django.utils import simplejson
# Create your models here.
class BaseDataManagerModel(models.Model):
    class Meta:
        abstract = True
        app_label = 'DataManager'

class Momend(BaseDataManagerModel):
    owner = models.ForeignKey(User)
    create_date = models.DateTimeField(auto_now_add=True)
    name = models.CharField(null=False, blank=False, max_length=255)
    thumbnail = models.CharField(max_length=2000, null=True, blank=True)


    momend_start_date = models.DateTimeField()
    momend_end_date = models.DateTimeField()

    #TODO stats
    PRIVACY_CHOICES = {
        'Private' : 0,
        'Public': 1,
        }
    privacy = models.IntegerField(choices=[[PRIVACY_CHOICES[key],key] for key in PRIVACY_CHOICES.keys()] , default=0)

    def __unicode__(self):
        return str(self.pk) + ' : ' + str(self.owner) + ':'+str(self.momend_start_date)+' - '+str(self.momend_end_date)

    def encode(self):
        enc = model_to_dict(self)
        layers = []
        for layer in AnimationLayer.objects.filter(momend=self, is_interaction=False):
            layers.append(layer.encode())
        enc['animation_layers'] = layers
        return enc

    def toJSON(self):
        return simplejson.dumps(self.encode(), default=lambda obj: obj.isoformat() if isinstance(obj, datetime) else None)

class AnimationLayer(BaseDataManagerModel):
    momend = models.ForeignKey(Momend)
    layer = models.IntegerField(null=True) #Like layer0, layer1 etc.
    description = models.CharField(max_length=255)
    is_interaction = models.BooleanField(default=False)


    def __unicode__(self):
        return str(self.momend)+' : '+str(self.layer)+'-'+str(self.description)

    def encode(self):
        enc = []
        for out in self.outdata_set.all():
            enc.append(out.encode())
        return enc

class Provider(BaseDataManagerModel):
    #any possible name for provider should match to the name of UserSocialAuth provider names
    name = models.CharField(max_length = 50)
    package_name = models.CharField(max_length = 255)
    module_name = models.CharField(max_length = 255)
    worker_name = models.CharField(max_length = 255)

    #this is used at DataManager::collect_user_data, reconsider changing
    def __unicode__(self):
        return str(self.name)

class RawData(BaseDataManagerModel):
    class Meta:
        verbose_name_plural = 'RawData'
        verbose_name = 'RawData'
        unique_together = ("original_id", "provider")

    owner = models.ForeignKey(User)

    original_path = models.CharField(max_length=2000) #original path of data if it exists
    original_id = models.CharField(max_length=255, db_index=True) #original id of data represents the source id
    data = models.TextField() #main data to use in momend
    title = models.CharField(max_length=255)
    thumbnail = models.CharField(max_length=2000, null=True, blank=True)

    DATA_TYPE= {'Photo': 0,
                'Status': 1,
                'Checkin': 2,
                'Background': 3,
                'Music' : 4, #NOT implemented yet, put here to be consistent with CoreAnimationData
    }
    type = models.IntegerField(choices=[[DATA_TYPE[key],key] for key in DATA_TYPE.keys()])

    provider = models.ForeignKey(Provider)


    create_date = models.DateTimeField(default = datetime.now)
    fetch_date = models.DateTimeField(auto_now_add = True)

    like_count = models.IntegerField(default = 0)
    comment_count = models.IntegerField(default = 0)
    share_count = models.IntegerField(default = 0)

    #TODO latitude,longitude etc.

    def __unicode__(self):
        return str(self.owner) + '_' + str(self.provider) + '_' + str(self.original_id)









