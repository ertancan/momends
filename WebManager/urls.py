__author__ = 'goktan'

from django.conf.urls import patterns
from django.conf.urls import url
from django.conf.urls import include
from django.views.generic.base import RedirectView
from django.core.urlresolvers import reverse_lazy
from views import HomePageFormView
from views import ShowMomendView
from views import GetMomendView
from views import SaveInteractionView
from django.contrib.auth.decorators import login_required
from registration.backends.default.urls import *
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = patterns('',

    #momends web manager urls
    url(r'^$', RedirectView.as_view(url=reverse_lazy('login')), name='front-page'),
    url(r'^home/$', login_required(HomePageFormView.as_view()), name='home-screen'),
    url(r'^show/(?P<id>\d+)/$', login_required(ShowMomendView.as_view()), name='show-momend'),
    url(r'^get/(?P<pk>\d+)/$', login_required(GetMomendView.as_view()), name='get-momend'),
    url(r'^postplay/(?P<id>\d+)/$', login_required(SaveInteractionView.as_view()), name='save-interaction'),
)
urlpatterns += staticfiles_urlpatterns()
