from Outputs.AnimationManager.ScenarioManager.ScenarioManagerWorker import ScenarioManagerWorker

__author__ = 'goktan'

from Outputs.BaseOutputWorker import BaseOutputWorker
from DataManager.models import Momend,RawData
from Outputs.AnimationManager.models import Theme,CoreAnimationData
from Outputs.AnimationManager.ThemeManager.ThemeManagerWorker import ThemeManagerWorker
from LogManagers.Log import Log
from DataManager.UserDataManager import UserDataManager

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
        self.user_data_manager = None

    def generate_output(self, enriched_data, duration, theme=None, scenario=None):
        """
        :param enriched_data: Data with criteria and its results for objects
        :param theme: Theme to be used or None if random
        :return: AnimationLayer[], duration
        """
        if not theme:
            theme = Theme.objects.order_by('?')[0]

        types = RawData.DATA_TYPE
        scenarioWorker = ScenarioManagerWorker()
        prepared_scenario, duration, used_bg_count, used_photo_count, used_status_count, used_checkin_count =\
        scenarioWorker.prepare_scenario(self.momend, duration, theme, scenario, max_photo=len(enriched_data[types['Photo']]),
            max_status=len(enriched_data[types['Status']]), max_checkin=len(enriched_data[types['Checkin']]), max_bg=len(enriched_data[types['Background']]), selection='random')

        try:
            self._validate_data_count(enriched_data, used_bg_count, used_photo_count, used_status_count, used_checkin_count)
        except DataCountException, e:
            Log.error(e.message)
            return False

        self.user_data_manager = UserDataManager(enriched_data)
        filled_scenario = self._fill_user_data(prepared_scenario['objects'])
        self._apply_theme(filled_scenario,theme,str(self.momend.pk))

        return filled_scenario, duration

    def _validate_data_count(self, enriched_data, used_bg_count, used_photo_count, used_status_count, used_checkin_count):
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

    def _fill_user_data(self, scenario):
        for object_layer in scenario:
            for outData in object_layer:
                used_type = outData.animation.used_object_type
                if used_type in CoreAnimationData.USER_DATA_KEYWORDS:
                    used_object = self.user_data_manager.get_data_for_keyword(used_type)
                    if used_object:
                        outData.raw = used_object.raw
                        outData.selection_criteria = used_object.criteria
                        outData.priority = used_object.priority
                elif used_type in CoreAnimationData.SPECIAL_DATA_KEYWORDS:
                    used_object = self.user_data_manager.get_data_for_keyword(used_type)
                    if used_object:
                        index = CoreAnimationData.SPECIAL_DATA_KEYWORDS.index(used_type)
                        if index == 0:  # Title
                            print 'USED--->'+str(used_object.raw)
                            print 'data:'+str(used_object.raw.data)
                            outData.raw = used_object.raw
                            outData.selection_criteria = 'Photo Title'
                            outData.priority = 100
                            outData.final_data_path = used_object.raw.data
                outData.save()
        return scenario

    def _apply_theme(self, scenario_layers, theme, prefix):
        themeWorker = ThemeManagerWorker(theme)
        for animation_layer in scenario_layers:
            for outdata in animation_layer:
                themeWorker.apply_theme(outdata, file_prefix=prefix)


    def save_output(self):
        pass

