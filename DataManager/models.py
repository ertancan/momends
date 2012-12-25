from django.db import models
from datetime import datetime
# Create your models here.
class BaseDataManagerModel(models.Model):
    class Meta:
        abstract = True
        app_label = 'DataManager'

class RawData(BaseDataManagerModel):
    path = models.CharField(max_length=500)
    _data_choices = (
        (0, 'Photo'),
        (1, 'Status'),
        (2, 'Checkin'),
        )
    type = models.IntegerField(choices=_data_choices)

    _source_choices = (
        (0,'Local'),
        (1,'Facebook'),
        (2,'Twitter'),
        (3,'Instagram')
    )
    source = models.IntegerField(choices=_source_choices)

    create_date = models.DateTimeField(default=datetime.now)
    fetch_date = models.DateTimeField(auto_now_add=True)

    like_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    share_count = models.IntegerField(default=0)

    #TODO latitude,longitude etc.

class EnrichedData(BaseDataManagerModel):
    pass





