# Django settings for momends project.

from local_settings import *

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/momends/static/'

# List of finder classes that know how to find static files in
# various locations.
#TODO(goktan): check http://django-storages.readthedocs.org/en/latest/backends/amazon-S3.html for s3
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'vsev71s2!p6$p^*oo3w%az3ram6@4dadmjpri@)19$*gacvvnz'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'momends.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'momends.wsgi.application'


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'DataManager',
    'ExternalProviders.FacebookProvider',
    'ExternalProviders.TwitterProvider',
    'ExternalProviders.InstagramProvider',
    'Outputs.AnimationManager',
    'Outputs.VideoManager',
    'WebManager',
    'social_auth',
)

#Settings for directories
ENHANCEMENT_SCRIPT_DIR = 'Outputs/AnimationManager/ThemeManager/enhancement_scripts/'
COLLECTED_FILE_PATH = 'userdata/collected/'
ENHANCED_FILE_PATH = 'userdata/enhanced/'

LOGIN_URL = '/login/'
LOGIN_ERROR_URL = '/login-error/'
LOGIN_REDIRECT_URL = '/momends/home/'

#Settings for social-auth
TWITTER_CONSUMER_KEY = '5DOIZsrFVxeL6L6dpsSBKg'
TWITTER_CONSUMER_SECRET = 't9xLkL2e4MdxWWbS5WlbH9z16BYNipTnKHQv0q7JHic'

FACEBOOK_APP_ID = '125999474230740'
FACEBOOK_API_SECRET = 'f68f2d67e320efc5e3790ae17004db7b'

AUTHENTICATION_BACKENDS = (
    'social_auth.backends.facebook.FacebookBackend',
    'django.contrib.auth.backends.ModelBackend',
    )

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'social_auth.context_processors.social_auth_by_type_backends',
    )

SOCIAL_AUTH_ENABLED_BACKENDS = ('facebook',)
SOCIAL_AUTH_DEFAULT_USERNAME = 'new_social_auth_user'
#SOCIAL_AUTH_COMPLETE_URL_NAME  = 'momends:home-screen'
#SOCIAL_AUTH_ASSOCIATE_URL_NAME = 'momends:home-screen'