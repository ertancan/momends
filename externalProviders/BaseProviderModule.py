__author__ = 'goktan'

from django.db import models

class BaseProviderModule(models.Model):
    class Meta:
        abstract = True
        app_label = 'DataManager'