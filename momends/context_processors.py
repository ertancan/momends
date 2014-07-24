__author__ = 'goktan'

def momend_file_url(request):
    from django.conf import settings
    return {'MOMEND_FILE_URL': settings.MOMEND_FILE_URL}

def theme_data_url(request):
    from django.conf import settings
    return {'THEME_DATA_URL': settings.THEME_DATA_PATH}

def host_url(request):
    from django.conf import settings
    return {'HOST_URL' : settings.HOST_URL}