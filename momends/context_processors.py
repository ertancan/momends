__author__ = 'goktan'

def momend_file_url(request):
    from django.conf import settings
    return {'MOMEND_FILE_URL': settings.MOMEND_FILE_URL}