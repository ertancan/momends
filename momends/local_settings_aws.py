__author__ = 'goktan'

#This file stands for keeping environment related settings. Each environment should have its own additional_settings file

DEBUG = True
TEMPLATE_DEBUG = DEBUG
from os import environ

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'host': environ['MYSQL_HOST'],
            'user': 'momends',
            'passwd': environ['MYSQL_PASSWORD'],
            'db': environ['MYSQL_DB'],
            'use_unicode': 'True',
            },
        }
}

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    #TODO(goktan) on production, check following line
    )


# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
        },

    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
            },
        'console':{
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'mail_admins': {
            'level': 'CRITICAL',
            'class': 'django.utils.log.AdminEmailHandler',
            },
        'loggly': {
            'level': 'DEBUG',
            'class': 'hoover.LogglyHttpHandler',
            'token': '8fa80082-6364-49be-bd01-9e60c53f7277',
            }

    },
    'loggers': {
        'momends': {
            'handlers': ['console', 'loggly'],
            'propagate': True,
            'level': 'DEBUG',
            },
        'django.request': {
            'handlers': ['console'],
            'level': 'CRITICAL',
            'propagate': False,
            }
    }
}

from os import environ
AWS_STORAGE_BUCKET_NAME = environ['AWS_STORAGE_BUCKET_NAME']
S3_URL = 'http://%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME
MOMEND_FILE_URL = S3_URL
TMP_FILE_PATH = '/tmp/momends_tmp/'
