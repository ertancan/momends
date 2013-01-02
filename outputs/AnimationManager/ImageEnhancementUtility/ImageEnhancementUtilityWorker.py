__author__ = 'ertan'
from django.conf import settings
import subprocess,os
from Outputs.AnimationManager.models import ImageEnhancement
class ImageEnhancementUtility(object):
    @staticmethod
    def applyThemeEnhancementsOnImage(filename,enhancement_str,file_prefix):

        os.environ['PATH'] += ':/usr/local/bin' #TODO: remove this on prod For mac os

        enhancement_objects = []
        enhancement_ids =enhancement_str.split(',')
        for enh_id in enhancement_ids:
            enhancement_objects.append(ImageEnhancement.objects.get(pk=int(enh_id)))

        current_filename = filename
        dot_index = filename.rindex('.')
        name_part = filename[:dot_index]
        ext_part = filename[dot_index:]

        if settings.COLLECTED_FILE_PATH in name_part:
            name_part = name_part[len(settings.COLLECTED_FILE_PATH):]

        i = 1
        for enhance in enhancement_objects:
            enh_out_filename = settings.ENHANCED_FILE_PATH + name_part +'_' + file_prefix + '_enh'+str(i)+ ext_part #name file as filename_enh1.ext etc.
            params =settings.ENHANCEMENT_SCRIPT_DIR+enhance.script_path +' '
            params += enhance.parameters
            params += ' '
            params += current_filename
            params += ' '
            params += enh_out_filename

            subprocess.call(params,shell=True,env=os.environ.copy()) #like ./script parameters input_file output_file

            if current_filename != filename: #Delete file if it won't be needed
                subprocess.call(['rm',current_filename])
            current_filename = enh_out_filename
            i += 1

        return current_filename