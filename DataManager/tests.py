"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase


from django.contrib.auth.models import User
from DataManager.DataManager import DataManager
from DataManager.models import Provider, RawData
from DataManager.DataEnrich.DataEnrichManager import DataEnrichManager
from datetime import datetime

ert = User.objects.get(username='ertan')
dm = DataManager(ert)
start = datetime.strptime('2012-01-01','%Y-%m-%d')
end = datetime.strptime('2012-05-01','%Y-%m-%d')
dm.create_momend(start,end,50)