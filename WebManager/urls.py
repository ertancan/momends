__author__ = 'goktan'

from django.conf.urls import patterns
from django.conf.urls import url
from views import HomePageLoggedFormView
from views import HomePageNotLoggedView
from views import MainRedirectView
from views import ShowMomendView
from views import GetMomendView
from views import SaveInteractionView
from views import UserProfileTemplateView
from views import SettingsFormView
from django.contrib.auth.decorators import login_required
from registration.backends.default.urls import *
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = patterns('',

    #momends web manager urls
    url(r'^$', MainRedirectView.as_view(), name='front-page'),  #redirect to /home if auth is ok, otherwise redirect to /main
    url(r'^main/$', HomePageNotLoggedView.as_view(), name='main-screen'),
    url(r'^home/$', login_required(HomePageLoggedFormView.as_view()), name='home-screen'),
    url(r'^user/(?P<id>\d+)/$', login_required(UserProfileTemplateView.as_view()), name='user-screen'),
    url(r'^user/(?P<username>\w+)/$', login_required(UserProfileTemplateView.as_view()), name='user-screen'),
    url(r'^settings/$', login_required(SettingsFormView.as_view()), name='settings-screen'),
    url(r'^show/(?P<type>\w{1})/(?P<id>\d+)/$', login_required(ShowMomendView.as_view()), name='show-momend'),
    url(r'^get/(?P<type>\w{1})/(?P<id>\d+)/$', login_required(GetMomendView.as_view()), name='get-momend'),
    url(r'^postplay/(?P<id>\d+)/$', login_required(SaveInteractionView.as_view()), name='save-interaction'),
)
urlpatterns += staticfiles_urlpatterns()
