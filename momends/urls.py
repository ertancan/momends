from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'momends.views.home', name='home'),
    # url(r'^momends/', include('momends.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    #enable DataManager views as momend's main views
    url(r'^momends/', include('WebManager.urls',namespace="momends")),

    #enable social-auth urls
    url(r'', include('social_auth.urls')),
)
