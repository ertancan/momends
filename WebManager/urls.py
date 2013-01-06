__author__ = 'goktan'

from django.conf.urls import patterns
from django.conf.urls import url
from django.views.generic.base import RedirectView
from django.core.urlresolvers import reverse_lazy
from views import HomePageFormView
from views import ShowMomendView
from views import GetMomendView
from views import FrontPageView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = patterns('',
    url(r'^$', FrontPageView.as_view(), name='front-page'),
    url(r'^home/$', HomePageFormView.as_view(), name='home-screen'),
    url(r'^show/(?P<id>\d+)/$', ShowMomendView.as_view(), name='show-momend'),
    url(r'^get/(?P<pk>\d+)/$', GetMomendView.as_view(), name='get-momend'),
)
urlpatterns += staticfiles_urlpatterns()
