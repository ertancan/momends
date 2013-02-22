# Django settings for momends project.

from os.path import abspath, dirname, basename
from distutils.sysconfig import get_python_lib
from os import environ


ROOT_PATH = abspath(dirname(__file__))
PROJECT_NAME = basename(ROOT_PATH)
PYTHON_LIB_DIR = get_python_lib()

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


# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for static files.
STATIC_URL = '/static/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = 'WebManager/static/'


# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'vsev71s2!p6$p^*oo3w%az3ram6@4dadmjpri@)19$*gacvvnz'


TEMPLATE_DIRS = (
    (ROOT_PATH + '/WebManager/templates'),
    (PYTHON_LIB_DIR + '/captcha/templates'),
    )


# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
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
    'django.contrib.admin',
    'DataManager',
    'ExternalProviders.FacebookProvider',
    'ExternalProviders.TwitterProvider',
    'ExternalProviders.InstagramProvider',
    'ExternalProviders.FileUploadProvider',
    'Outputs.AnimationManager',
    'Outputs.VideoManager',
    'WebManager',
    'social_auth',
    'registration',
    'sorl.thumbnail',
)


LOGIN_URL = '/main/'
LOGIN_ERROR_URL = '/accounts/login-error/'
LOGIN_REDIRECT_URL = '/home/'

FACEBOOK_APP_ID = environ.get('FACEBOOK_APP_ID')
FACEBOOK_API_SECRET = environ.get('FACEBOOK_API_SECRET')
FACEBOOK_EXTENDED_PERMISSIONS = ['email', 'user_about_me', 'user_activities', 'user_location', 'user_photos', 'user_status']

TWITTER_CONSUMER_KEY = environ.get('TWITTER_CONSUMER_KEY')
TWITTER_CONSUMER_SECRET = environ.get('TWITTER_CONSUMER_SECRET')

AUTHENTICATION_BACKENDS = (
    'social_auth.backends.twitter.TwitterBackend',
    'social_auth.backends.facebook.FacebookBackend',
    'django.contrib.auth.backends.ModelBackend',
    )

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.contrib.messages.context_processors.messages',
    'social_auth.context_processors.social_auth_by_type_backends',
    'momends.context_processors.momend_file_url',
    'momends.context_processors.theme_data_url',
    'momends.context_processors.host_url',
    'django.core.context_processors.request',
    )

SOCIAL_AUTH_PIPELINE = (
    'social_auth.backends.pipeline.social.social_auth_user',
    'social_auth.backends.pipeline.associate.associate_by_email',
    'social_auth.backends.pipeline.user.get_username',
    'social_auth.backends.pipeline.user.create_user',
    'social_auth.backends.pipeline.social.associate_user',
    'social_auth.backends.pipeline.social.load_extra_data',
    'social_auth.backends.pipeline.user.update_user_details'
    )

SOCIAL_AUTH_ENABLED_BACKENDS = ('facebook','twitter',)
SOCIAL_AUTH_DEFAULT_USERNAME = 'new_social_auth_user'
SOCIAL_AUTH_SESSION_EXPIRATION = False
#SOCIAL_AUTH_COMPLETE_URL_NAME  = home-screen'
#SOCIAL_AUTH_ASSOCIATE_URL_NAME = 'home-screen'

#registration framework
ACCOUNT_ACTIVATION_DAYS = 7

#captcha framework
#https://www.google.com/recaptcha/admin/site?siteid=316357769
RECAPTCHA_PUBLIC_KEY = environ.get('RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY = environ.get('RECAPTCHA_PRIVATE_KEY')
#RECAPTCHA_USE_SSL = True


DATABASE_OPTIONS = {
    'use_unicode': True,
    'charset': 'utf8'
}

RUNNING_SERVER = environ.get('MOMENDS_HOST')
if  RUNNING_SERVER == 'dev':
    from local_settings import *
elif environ['MOMENDS_HOST'] == 'prod':
    from local_settings_aws import *
else:
    raise Exception


