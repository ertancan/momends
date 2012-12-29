from Outputs.AnimationManager.ScenarioManager.ScenarioManagerWorker import ScenarioManagerWorker

__author__ = 'goktan'

from Outputs.BaseOutputWorker import BaseOutputWorker
from DataManager.models import Momend, Theme,OutData
from Outputs.AnimationManager.ThemeManager.ThemeManagerWorker import ThemeManagerWorker

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

        scenarioWorker = ScenarioManagerWorker()
        prepared_scenario, duration, used_bg_count, used_photo_count, used_status_count, used_checkin_count = scenarioWorker.prepare_scenario(self.momend, duration, theme,scenario)
        try:
            self._validate_data_count(enriched_data, used_bg_count, used_photo_count, used_status_count, used_checkin_count)
        except DataCountException, e:
            print(e.message)
            return False

        filled_scenario = self._fill_user_data(prepared_scenario['objects'], enriched_data)

        themeWorker = ThemeManagerWorker(theme)
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

        #TODO: CORRECT HERE WITH SWITCH CASE
        for level in scenario:
            for animation_object in level:
                assert isinstance(animation_object,OutData)
                used_enriched_object = None
                object_type = animation_object.animation.used_object_type
                if object_type == '{{USER_PHOTO}}' or object_type == '{{NEXT_USER_PHOTO}}':
                    if len(object_type) > 15: #Not to compare strings again (This is NEXT_USER_PHOTO)
                        photo_index += 1
                    used_enriched_object = enriched_data['photo'][photo_index]
                if object_type == '{{USER_STATUS}}' or object_type == '{{NEXT_USER_STATUS}}':
                    if len(object_type) >17:
                        status_index += 1
                    used_enriched_object = enriched_data['status'][status_index]
                if object_type == '{{USER_CHECKIN}}' or object_type == '{{NEXT_USER_CHECKIN}}':
                    if len(object_type) > 18:
                        checkin_index += 1
                    used_enriched_object = enriched_data['checkin'][checkin_index]
                if object_type == '{{USER_BACKGROUND}}' or object_type == '{{NEXT_USER_BACKGROUND}}':
                    if len(object_type) > 21:
                        bg_index += 1
                    used_enriched_object = enriched_data['background'][bg_index]

                if used_enriched_object:
                    animation_object.raw = used_enriched_object.raw
                    animation_object.selection_criteria = used_enriched_object.criteria
                    animation_object.priority = used_enriched_object.priority

                animation_object.save() #Outside of the if, because they aren't saved before

        return scenario

    def save_output(self): #TODO save to db
        pass




