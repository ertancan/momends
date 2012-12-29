__author__ = 'ertan'
from Outputs.AnimationManager.models import ThemeData,ImageEnhancement
import subprocess
class ThemeManagerWorker:
    ENHANCEMENT_SCRIPT_DIR = 'enhancement_scripts/'
    def __init__(self,theme):
        self.theme = theme

    def apply_theme(self, outData_layers):
        """
        :param outData_layers: Layers to apply the theme enhancements and fill with theme data
        :param theme: theme to be used
        :return: outData_layers filled with theme data and enhanced images
        """
        filled_layers = self._fill_theme_data(outData_layers)
        enhanced_layers = self._apply_image_enhancement(outData_layers)
        return enhanced_layers


    def _fill_theme_data(self, outdata_layers):
        theme_assets = ThemeData.objects.filter(theme=self.theme)
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
                    outData.final_data_path = theme_assets[obj_type][current_indexes[obj_type]].data_path
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

    def _apply_image_enhancement(self,outdata_layers):
        image_enhancements_str = self.theme.image_enhancement_functions
        image_enhancements_ids =image_enhancements_str.split(',')
        enhancement_objects = []
        for enh_id in image_enhancements_ids:
            enhancement_objects.append(ImageEnhancement.objects.get(pk=int(enh_id)))

        for object_layer in outdata_layers:
            for outData in object_layer:
                if outData.animation.used_object_type in ['{{USER_PHOTO}}','{{NEXT_USER_PHOTO}}']: #TODO should we apply enhancement on background, too?
                    raw_filename= outData.raw.data
                    last_filename = raw_filename
                    dot_index = last_filename.rindex('.')
                    name_part = last_filename[:dot_index]
                    ext_part = last_filename[dot_index:]
                    i = 1
                    for enhance in enhancement_objects:
                        enh_out_filename = name_part + '_enh'+str(i)+ ext_part #name file as filename_enh1.ext etc.
                        subprocess.call([ImageEnhancement.ENHANCEMENT_SCRIPT_DIR+enhance.script_path, enhance.parameters, last_filename, enh_out_filename]) #like ./script parameters input_file output_file

                        if last_filename != raw_filename: #Delete file if it won't be needed
                            subprocess.call(['rm',last_filename])
                        last_filename = enh_out_filename
                        i += 1

                    outData.final_data_path = last_filename #Update final data with enhanced one
                    outData.save()
        return outdata_layers
