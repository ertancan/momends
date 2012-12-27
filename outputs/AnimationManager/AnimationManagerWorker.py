__author__ = 'goktan'

from Outputs.BaseOutputWorker import BaseOutputWorker
from DataManager.models import Momend,Scenario,Theme,OutData,RawData
from DataManager.ScenarioManager import ScenarioManagerWorker
from DataManager.ThemeManager import ThemeManagerWorker

class DataCountException(Exception):
    PHOTO_TYPE = 0
    STATUS_TYPE = 1
    CHECKIN_TYPE = 2
    BACKGROUND_TYPE = 3

    def __init__(self,missing_type):
        Exception.__init__(self,'Not enough data')
        self.type = missing_type

class AnimationManagerWorker(BaseOutputWorker):
    def __init__(self,momend):
        assert isinstance(momend, Momend)
        self.momend = momend

    def generate_output(self, enriched_data, duration, theme=None, scenario=None):
        """
        :param enriched_data: Data with criteria and its results for objects
        :param theme: Theme to be used or None if random
        :return: AnimationLayer[]
        """
        if not theme:
            theme = Theme.objects.order_by('?')[0]

        scenarioWorker = ScenarioManagerWorker.ScenarioManagerWorker()
        prepared_scenario, duration, used_bg_count, used_photo_count, used_status_count, used_checkin_count = scenarioWorker.prepare_scenario(duration,theme,scenario)
        try:
            self._validate_data_count(enriched_data, used_bg_count, used_photo_count, used_status_count, used_checkin_count)
        except DataCountException, e:
            print(e.message)
            return False

        for layer in prepared_scenario: #Set layer momend, ScenarioManager doesn't know the momend
            layer.momend = self.momend

        filled_scenario = self._fill_user_data(prepared_scenario,enriched_data)

        themeWorker = ThemeManagerWorker.ThemeManagerWorker()
        self.animation = themeWorker.apply_theme(filled_scenario)
        return self.animation

    def _validate_data_count(self,enriched_data, used_bg_count, used_photo_count, used_status_count, used_checkin_count):
        if len(enriched_data['photo']) < used_photo_count:
            raise DataCountException(DataCountException.PHOTO_TYPE)
        if len(enriched_data['status']) < used_status_count:
            raise DataCountException(DataCountException.STATUS_TYPE)
        if len(enriched_data['checkin']) < used_checkin_count:
            raise DataCountException(DataCountException.CHECKIN_TYPE)
        if len(enriched_data['background']) < used_bg_count:
            raise DataCountException(DataCountException.BACKGROUND_TYPE)
        return True

    def _fill_user_data(self,scenario,enriched_data):
        photo_index = 0
        status_index = 0
        checkin_index = 0
        bg_index = 0

        for level in scenario:
            for animation_object in level:
                assert isinstance(animation_object,OutData)
                used_enriched_object = None
                if animation_object.animation.used_object_type == '{{USER_PHOTO}}':
                    used_enriched_object = enriched_data['photo'][photo_index]
                    photo_index += 1
                if animation_object.animation.used_object_type == '{{USER_STATUS}}':
                    used_enriched_object = enriched_data['status'][status_index]
                    status_index += 1
                if animation_object.animation.used_object_type == '{{USER_CHECKIN}}':
                    used_enriched_object = enriched_data['checkin'][checkin_index]
                    checkin_index += 1
                if animation_object.animation.used_object_type == '{{USER_BACKGROUND}}':
                    used_enriched_object = enriched_data['background'][bg_index]
                    bg_index += 1

                if used_enriched_object:
                    animation_object.raw = used_enriched_object.raw
                    animation_object.selection_criteria = used_enriched_object.criteria
                    animation_object.priority = used_enriched_object.priority

        return scenario

    def save_output(self): #TODO save to db
        pass




