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
    """
    Async momend create task
    Delegates creation steps to DataManager
    @param duration: approximate! duration of the momend (in seconds)
    @param mail: False; do not send mail to the owner after create
    @param name: name of the momend. uses directly if given, creates one if not
    @param theme: Theme to be used on the momend, None for random
    @param scenario: Should be given if any specific scenario should be used
    @param inc_photo: Whether we should use photos while creating the momend or not
    @param inc_status: Whether we should use statuses while creating the momend or not
    @param inc_checkin: Whether we should use checkins or while creating the momend not
    @param enrichment_method what kind of enrichment should be used on user data. Decides automatically if None

    uses parameters from kwargs
    selected: Indicates selected photos, won't collect photos from providers
    friends: Selected friends to filter
    chronological: Preserve chronological order
    """
    _create_start = time.time()
    _user = User.objects.get(pk=user_id)
    _momend = Momend.objects.get(pk=momend_id)
    _status = MomendStatus.objects.get(momend=_momend)
    dm = DataManager.DataManager(_user, _momend, _status)
    try:
        _status.status = MomendStatus.MOMEND_STATUS['Collecting Data']
        _status.save()
        raw_data, collect_status = dm.collect_user_data(inc_photo, inc_status, inc_checkin, **kwargs)

        if kwargs['selected']:  # Do not filter or enrich user selected data
            enriched_data = dm.encapsulate_raw_data(raw_data)
        else:
            # Filter collected data according to the parameters
            _enrich_filter = dict()
            _enrich_filter['friends'] = kwargs['friends']
            _enrich_filter['chronological'] = kwargs['chronological']
            enriched_data = dm.enrich_user_data(raw_data, _enrich_filter, enrichment_method)

        # Collected item count check
        _photo_count = len(enriched_data[RawData.DATA_TYPE['Photo']])
        if _photo_count < 10:
            if kwargs['selected']:
                dm._handle_momend_create_error('You selected less than 10 photos. Please select more')
            elif kwargs['friends']:
                if _photo_count == 0:
                    dm._handle_momend_create_error('You don\'t have any photos together! Please select a wider time frame')
                else:
                    dm._handle_momend_create_error('You don\'t have enough photos together! Please select a wider time frame', 'Has only ' + str(len(enriched_data[RawData.DATA_TYPE['Photo']])) + ' photos')
            else:
                if _photo_count == 0:
                    dm._handle_momend_create_error('Could not collect any photos! Please select a wider time frame')
                else:
                    dm._handle_momend_create_error('Only ' + str(_photo_count) + ' photos collected! Please select a wider time frame')
            return None

        _status.status = MomendStatus.MOMEND_STATUS['Applying Enhancements']
        _status.save()

        animation_worker = AnimationManagerWorker(_momend)
        generated_layer, duration = animation_worker.generate_output(enriched_data, duration, theme, scenario)
        if duration == 0 or not generated_layer:
            dm._handle_momend_create_error('Something went wrong while generating your momend! Please try again.', 'Created momend duration is 0')
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
