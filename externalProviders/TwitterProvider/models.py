from django.db import models
from ExternalProviders.BaseProviderModule import BaseProviderModule

class TwitterProviderModule(BaseProviderModule):
    user_secret = models.TextField()