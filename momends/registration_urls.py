#this file have been adopted from /venv/lib/python2.7/site-packages/registration/backends/default/urls.py
#and /venv/lib/python2.7/site-packages/registration/auth_urls.py
#copied in order to enhance url's with captcha and enhanced forms

__author__ = 'goktan'
from django.conf.urls import patterns
from django.conf.urls import url
from django.conf.urls import include
from django.views.generic.simple import direct_to_template
from django.contrib.auth import views as auth_views
from registration.views import activate
from registration.views import register
from momends.forms import *

urlpatterns = patterns('',
    url(r'^activate/complete/$',
        direct_to_template,
        {'template': 'registration/activation_complete.html'},
        name='registration_activation_complete'),
    # Activation keys get matched by \w+ instead of the more specific
    # [a-fA-F0-9]{40} because a bad activation key should still get to the view;
    # that way it can return a sensible "invalid key" message instead of a
    # confusing 404.
    url(r'^activate/(?P<activation_key>\w+)/$',
        activate,
        {'backend': 'registration.backends.default.DefaultBackend',
         },
        name='registration_activate'),
    url(r'^register/$',
        register,
        {'backend': 'registration.backends.default.DefaultBackend',
         'form_class': RegistrationFormCaptcha
        },
        name='registration_register'),
    url(r'^register/complete/$',
        direct_to_template,
        {'template': 'registration/registration_complete.html'},
        name='registration_complete'),
    url(r'^register/closed/$',
        direct_to_template,
        {'template': 'registration/registration_closed.html'},
        name='registration_disallowed'),
    #(r'', include('registration.auth_urls')),
)

urlpatterns += patterns('',
    url(r'^login/$',
        auth_views.login,
        {'template_name': 'registration/login.html'},
        name='auth_login'),
    url(r'^logout/$',
        auth_views.logout_then_login,
        name='auth_logout'),
    url(r'^password/change/$',
        auth_views.password_change,
        name='auth_password_change'),
    url(r'^password/change/done/$',
        auth_views.password_change_done,
        name='auth_password_change_done'),
    url(r'^password/reset/$',
        auth_views.password_reset,
        name='auth_password_reset'),
    url(r'^password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
        auth_views.password_reset_confirm,
        name='auth_password_reset_confirm'),
    url(r'^password/reset/complete/$',
        auth_views.password_reset_complete,
        name='auth_password_reset_complete'),
    url(r'^password/reset/done/$',
        auth_views.password_reset_done,
        name='auth_password_reset_done'),
)

