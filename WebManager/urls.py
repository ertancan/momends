__author__ = 'goktan'

from django.conf.urls import patterns
from django.conf.urls import url
from django.views.generic.base import RedirectView
from django.core.urlresolvers import reverse_lazy
from views import HomePageFormView

import views

urlpatterns = patterns('',
    url(r'^$', RedirectView.as_view(url=reverse_lazy('momends:home-screen')), name='front-page'),
    url(r'^home/$', HomePageFormView.as_view(), name='home-screen'),
)
