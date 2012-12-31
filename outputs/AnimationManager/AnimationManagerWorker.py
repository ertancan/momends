from Outputs.AnimationManager.ScenarioManager.ScenarioManagerWorker import ScenarioManagerWorker

__author__ = 'goktan'

from Outputs.BaseOutputWorker import BaseOutputWorker
from DataManager.models import Momend,RawData,CoreAnimationData
from Outputs.AnimationManager.models import Theme
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

        types = RawData.DATA_TYPE
        scenarioWorker = ScenarioManagerWorker()
        prepared_scenario, duration, used_bg_count, used_photo_count, used_status_count, used_checkin_count =\
        scenarioWorker.prepare_scenario(self.momend, duration, theme, scenario, max_photo=len(enriched_data[types['Photo']]),
            max_status=len(enriched_data[types['Status']]), max_checkin=len(enriched_data[types['Checkin']]), max_bg=len(enriched_data[types['Background']]))

        try:
            self._validate_data_count(enriched_data, used_bg_count, used_photo_count, used_status_count, used_checkin_count)
        except DataCountException, e:
            print(e.message)
            return False

        filled_scenario = self._fill_user_data(prepared_scenario['objects'], enriched_data)

        themeWorker = ThemeManagerWorker(theme)
        self.animation = themeWorker.apply_theme(filled_scenario,file_prefix=str(self.momend.pk))
        return self.animation

    def _validate_data_count(self,enriched_data, used_bg_count, used_photo_count, used_status_count, used_checkin_count):
        types = RawData.DATA_TYPE
        if len(enriched_data[types['Photo']]) < used_photo_count:
            raise DataCountException(DataCountException.PHOTO_TYPE)
        if len(enriched_data[types['Status']]) < used_status_count:
            raise DataCountException(DataCountException.STATUS_TYPE)
        if len(enriched_data[types['Checkin']]) < used_checkin_count:
            raise DataCountException(DataCountException.CHECKIN_TYPE)
        if len(enriched_data[types['Background']]) < used_bg_count:
            raise DataCountException(DataCountException.BACKGROUND_TYPE)
        return True

    def _fill_user_data(self,scenario,enriched_data):
        keywords = CoreAnimationData.USER_DATA_TYPE
        current_indexes = [-1 for i in range(1,len(keywords)/2)] # For -1 array?
        for object_layer in scenario:
            for outData in object_layer:
                used_type = outData.animation.used_object_type
                if used_type in keywords:
                    index = keywords.index(used_type)
                    obj_type = index/2
                    should_increase = index % 2 == 1
                    if (should_increase or current_indexes[obj_type] == -1) and\
                       current_indexes[obj_type] < len(enriched_data[obj_type]) -1: #No one wanted a data in this type before. Actually a misuse.
                        current_indexes[obj_type] += 1
                    used_object = enriched_data[obj_type][current_indexes[obj_type]]
                    outData.raw = used_object.raw
                    outData.selection_criteria = used_object.criteria
                    outData.priority = used_object.priority
                outData.save()
        return  scenario

    def save_output(self): #TODO save to db
        pass




