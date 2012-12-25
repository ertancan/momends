from django.db import models
from datetime import datetime
# Create your models here.
class BaseDataManagerModel(models.Model):
    class Meta:
        abstract = True
        app_label = 'DataManager'


class Provider(BaseDataManagerModel):
    name = models.CharField(max_length = 50)
    package_name = models.CharField(max_length = 255)
    module_name = models.CharField(max_length = 255)
    worker_name = models.CharField(max_length = 255)

class RawData(BaseDataManagerModel):
    path = models.CharField(max_length = 500)
    original_id = models.TextField()
    data = models.TextField()

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

class EnrichedData(BaseDataManagerModel):
    pass





