__author__ = 'ertan'
from DataManager.models import ThemeData
class ThemeManagerWorker:
    def __init__(self,theme):
        self.theme = theme

    def apply_theme(self, outData_layers):
        """
        :param outData_layers: Layers to apply the theme enhancements and fill with theme data
        :param theme: theme to be used
        :return: outData_layers filled with theme data and enhanced images
        """
        filled_layers = self._fill_theme_data(outData_layers)
        return filled_layers


    def _fill_theme_data(self, outdata_layers):
        theme_assets = ThemeData.objects.filter(theme= self.theme)
        theme_assets = self._group_theme_data(theme_assets)
        keywords = ThemeData.THEME_DATA_TYPE_KEYWORDS
        current_indexes = [-1 for i in range(1,len(ThemeData.THEME_DATA_TYPE))] # For -1 array?
        for object_layer in outdata_layers:
            for outData in object_layer:
                used_type = outData.animation.used_object_type
                if used_type in keywords:
                    index = keywords.index(used_type)
                    obj_type = index/2
                    should_increase = index % 2 == 1
                    if (should_increase or current_indexes[obj_type] == -1) and \
                       current_indexes[obj_type] < len(theme_assets[obj_type]) -1: #No one wanted a data in this type before. Actually a misuse.
                        current_indexes[obj_type] += 1
                    outData.out_data = theme_assets[obj_type][current_indexes[obj_type]].data_path
                    outData.selection_criteria = 'Theme Asset'
                    outData.save() #Update db

    def _group_theme_data(self,theme_data):
        types = ThemeData.THEME_DATA_TYPE
        result = []
        for i in range(0,len(types)):
            result.append([])

        for data in theme_data:
            result[data.type].append(data)

        return result
