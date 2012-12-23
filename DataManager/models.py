from django.db import models

# Create your models here.

class BaseDataManagerModel(models.Model):
    class Meta:
        abstract = True
        app_label = 'DataManager'

class RawData(BaseDataManagerModel):
    pass

class EnrichedData(BaseDataManagerModel):
    pass





