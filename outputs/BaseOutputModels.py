__author__ = 'goktan'

from django.db import models

class BaseOutputModel(models.Model):
    class Meta:
        abstract = True
        app_label = 'DataManager'

class BaseMomendsDataModel(models.Model):
    class Meta:
        abstract = True
        app_label = 'DataManager'