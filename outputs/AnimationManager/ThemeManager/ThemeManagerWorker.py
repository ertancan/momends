__author__ = 'ertan'
from Outputs.AnimationManager.models import ThemeData,ImageEnhancement
from django.conf import settings
import subprocess,os
class ThemeManagerWorker:

    def __init__(self,theme):
        self.theme = theme

    def apply_theme(self, outData_layers,file_prefix):
        """
        :param outData_layers: Layers to apply the theme enhancements and fill with theme data
        :param theme: theme to be used
        :return: outData_layers filled with theme data and enhanced images
        """
        filled_layers = self._fill_theme_data(outData_layers)
        enhanced_layers = self._apply_image_enhancement(filled_layers,file_prefix)
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
        return  outdata_layers

    def _group_theme_data(self,theme_data):
        types = ThemeData.THEME_DATA_TYPE
        result = []
        for i in range(0,len(types)):
            result.append([])

        for data in theme_data:
            result[data.type].append(data)

        return result

    def _apply_image_enhancement(self,outdata_layers,file_prefix):
        image_enhancements_str = self.theme.image_enhancement_functions
        if image_enhancements_str == '':
            return
        os.environ['PATH'] += ':/usr/local/bin' #TODO: remove this on prod For mac os

        image_enhancements_ids =image_enhancements_str.split(',')

        enhancement_objects = []
        for enh_id in image_enhancements_ids:
            enhancement_objects.append(ImageEnhancement.objects.get(pk=int(enh_id)))

        applied_objects = dict()
        for object_layer in outdata_layers:
            for outData in object_layer:
                if outData.animation.used_object_type in ['{{USER_PHOTO}}','{{NEXT_USER_PHOTO}}']: #TODO should we apply enhancement on background, too?
                    raw_filename= outData.raw.data
                    if raw_filename in applied_objects: #Don't apply enhancement on the same object twice
                        outData.final_data_path = applied_objects[raw_filename]
                        continue

                    last_filename = raw_filename
                    dot_index = last_filename.rindex('.')
                    name_part = last_filename[:dot_index]
                    ext_part = last_filename[dot_index:]

                    if settings.COLLECTED_FILE_PATH in name_part:
                        name_part = name_part[len(settings.COLLECTED_FILE_PATH):]

                    i = 1
                    for enhance in enhancement_objects:
                        enh_out_filename = settings.ENHANCED_FILE_PATH + name_part +'_' + file_prefix + '_enh'+str(i)+ ext_part #name file as filename_enh1.ext etc.
                        params =settings.ENHANCEMENT_SCRIPT_DIR+enhance.script_path +' '
                        params += enhance.parameters
                        params += ' '
                        params += last_filename
                        params += ' '
                        params += enh_out_filename

                        subprocess.call(params,shell=True,env=os.environ.copy()) #like ./script parameters input_file output_file

                        if last_filename != raw_filename: #Delete file if it won't be needed
                            subprocess.call(['rm',last_filename])
                        last_filename = enh_out_filename
                        i += 1

                    outData.final_data_path = last_filename #Update final data with enhanced one
                    applied_objects[raw_filename] = last_filename
                    outData.save()
        return outdata_layers
