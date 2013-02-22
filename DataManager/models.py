from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from django.utils import simplejson
from Crypto.Cipher import AES
from django.conf import settings
import string
from LogManagers.Log import Log
from django.db.models.signals import pre_save


import base64
import random
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
    cryptic_id = models.CharField(max_length=255, null=True, blank=True)

    momend_start_date = models.DateTimeField(null=True)
    momend_end_date = models.DateTimeField(null=True)

    #TODO stats
    PRIVACY_CHOICES = {
        'Private' : 0,
        'Public': 1,
        }
    privacy = models.IntegerField(choices=[[PRIVACY_CHOICES[key],key] for key in PRIVACY_CHOICES.keys()] , default=0)

    def __unicode__(self):
        return str(self.pk) + ' : ' + str(self.owner) + ':'+str(self.momend_start_date)+' - '+str(self.momend_end_date)

    def encode(self):
        enc = model_to_dict(self,exclude=['owner'])
        enc['owner'] = dict(id=self.owner.id, username=self.owner.username)
        layers = []
        for layer in AnimationLayer.objects.filter(momend=self, is_interaction=False):
            layers.append(layer.encode())
        enc['animation_layers'] = layers
        return enc

    def toJSON(self):
        return simplejson.dumps(self.encode(), default=lambda obj: obj.isoformat() if isinstance(obj, datetime) else None)

def generate_cryptic_id_for_momend(sender,instance,using,**kwargs):
    if not instance.cryptic_id:
        instance.cryptic_id = encode_id(instance.pk)

pre_save.connect(generate_cryptic_id_for_momend, Momend)

class DeletedMomend(BaseDataManagerModel):
    #From Momend
    owner = models.ForeignKey(User)
    create_date = models.DateTimeField(auto_now_add=True)
    name = models.CharField(null=False, blank=False, max_length=255)
    thumbnail = models.CharField(max_length=2000, null=True, blank=True)
    momend_start_date = models.DateTimeField()
    momend_end_date = models.DateTimeField()
    privacy = models.IntegerField(choices=[[Momend.PRIVACY_CHOICES[key],key] for key in Momend.PRIVACY_CHOICES.keys()] , default=0)

    play_count = models.IntegerField(default=0)
    delete_date = models.DateTimeField(auto_now_add=True)

    def set_momend_data(self, original):
        self.owner = original.owner
        self.create_date = original.create_date
        self.name = original.name
        self.thumbnail = original.thumbnail #TODO we may not need it
        self.momend_start_date = original.momend_start_date
        self.momend_end_date = original.momend_end_date
        self.play_count = original.animationplaystat_set.count()

class MomendScore(BaseDataManagerModel):
    momend = models.OneToOneField(Momend)

    provider_score = models.IntegerField(default=0)
    #TODO view score etc.

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
        unique_together = ('owner', 'original_id', 'provider')

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

    @property
    def key_generate(self):
        """returns a string based unique key with length 80 chars, used for raw data without unique id"""
        while 1:
            key = str(random.getrandbits(256))
            try:
                RawData.objects.get(original_id=key)
            except:
                return key

def encode_id(id):
    if not id:
        return None
    pad = lambda s: s + (16 - len(s) % 16 ) * '}' #append '}'s to make the length a multiple of 8 (Block size)
    _cipher = AES.new(settings.SECRET_KEY[:16])
    _plain = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(5)) + str(id) #generate fixed length (5) random nonce and append the id as text
    #This will result a string like XXXXX6 where X's are random letters or digits and 6 is id. Fixed length is important to be able to decode it later
    _encrypted = _cipher.encrypt(pad(_plain))
    return base64.urlsafe_b64encode(_encrypted) #returning as base64 string to use as url parameter

def decode_id(cryptic_id):
    Log.debug('Decode this: '+cryptic_id)
    _cipher = AES.new(settings.SECRET_KEY[:16])
    try:
        _encrypted = base64.urlsafe_b64decode(cryptic_id.encode('utf-8'))
    except TypeError as te:
        Log.warn('Invalid base64 on url:'+str(te))
        return None
    try:
        _plain = _cipher.decrypt(_encrypted).rstrip('}') #Decrypt and remove the padding ('}')
    except ValueError:
        Log.warn('Invalid cipher text')
        return None
    try:
        _id = _plain[5:] #Take the part after the fixed length nonce
        return int(_id)
    except ValueError:
        Log.fatal('Someone tried to forge an id')
        return None








