__author__ = 'goktan'

from django.db import models
from django.contrib.auth.models import User

class BaseProviderModule(models.Model):
    class Meta:
        abstract = True
        app_label = 'DataManager'

    owner = models.ForeignKey(User)
    token = models.TextField()