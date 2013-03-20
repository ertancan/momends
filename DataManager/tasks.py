__author__ = 'ertan'
"""
    Contains Async tasks which will be handled by Celery
"""
from celery import task
import DataManager
from models import *
from django.contrib.auth.models import User
from Outputs.AnimationManager.AnimationManagerWorker import AnimationManagerWorker
import traceback
from DataManagerUtil import DataManagerUtil
import time


@task()
def create_momend_task(user_id, momend_id, duration, mail, theme, scenario, inc_photo, inc_status, inc_checkin, enrichment_method, **kwargs):
    _create_start = time.time()
    _user = User.objects.get(pk=user_id)
    _momend = Momend.objects.get(pk=momend_id)
    _status = MomendStatus.objects.get(momend=_momend)
    dm = DataManager.DataManager(_user, _momend, _status)
    try:
        _status.status = MomendStatus.MOMEND_STATUS['Collecting Data']
        _status.save()
        raw_data, collect_status = dm.collect_user_data(inc_photo, inc_status, inc_checkin, **kwargs)
        if len(raw_data) < 15:
            dm._handle_momend_create_error('Could not collect enough data to create a momend! Please select a wider time frame')
            return None

        _enrich_filter = dict()
        if 'friends' in kwargs:
            _enrich_filter['friends'] = kwargs['friends']
        enriched_data = dm.enrich_user_data(raw_data, _enrich_filter, enrichment_method)
        _photo_count = len(enriched_data[RawData.DATA_TYPE['Photo']]) < 15
        if _photo_count < 15:
            if 'friends' in kwargs and kwargs['friend']:
                if _photo_count < 10:
                    dm._handle_momend_create_error('You don\'t have enough photos together! Please select a wider time frame', 'Has only ' + str(len(enriched_data[RawData.DATA_TYPE['Photo']])) + ' photos')
                    return None
            else:
                dm._handle_momend_create_error('Could not collect enough data to create a momend! Please select a wider time frame')

        _status.status = MomendStatus.MOMEND_STATUS['Applying Enhancements']
        _status.save()

        animation_worker = AnimationManagerWorker(_momend)
        generated_layer, duration = animation_worker.generate_output(enriched_data, duration, theme, scenario)
        if duration == 0 or not generated_layer:
            dm._handle_momend_create_error('Could not create momend! Please try again.', 'Created momend duration is 0')
            return None
        dm._create_momend_thumbnail()
        _momend.save()

        score = MomendScore(momend=_momend, provider_score=dm._calculate_provider_score())
        score.save()
        if mail:
            DataManagerUtil.send_momend_created_email(_momend)
        _status.status = MomendStatus.MOMEND_STATUS['Success']
        _status.save()
        Log.info('Momend created in: '+str(time.time() - _create_start))

    except Exception as e:
        dm._handle_momend_create_error('Error while creating the momend. Please try again!', 'Exception: '+str(e)[:255])
        Log.error(traceback.format_exc())
