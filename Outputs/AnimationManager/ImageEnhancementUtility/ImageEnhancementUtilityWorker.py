__author__ = 'ertan'
from django.conf import settings
import subprocess,os
from Outputs.AnimationManager.models import ImageEnhancement
import shutil
from LogManagers.Log import Log

class ImageEnhancementUtility(object):
    @staticmethod
    def applyThemeEnhancementsOnImage(filename, enhancement_str, file_prefix, theme_data_manager):
        if len(enhancement_str) == 0:
            return filename
        os.environ['PATH'] += ':/usr/local/bin' #TODO: remove this on prod For mac os
        enhancement_objects = []
        enhancement_ids =enhancement_str.split(',')
        for enh_id in enhancement_ids:
            enhancement_objects.append(ImageEnhancement.objects.get(pk=int(enh_id)))

        _tmp_filename = filename
        try:
            dot_index = filename.rindex('.')
            name_part = filename[:dot_index]
            ext_part = filename[dot_index:]
        except ValueError:
            name_part = filename
            ext_part = ''  #there is no extension, unlikely but possible

        if settings.COLLECTED_FILE_PATH in name_part:
            name_part = name_part[len(settings.SAVE_PREFIX) + len(settings.COLLECTED_FILE_PATH):]

        for i, enhance in enumerate(enhancement_objects):
            _enhancement_parameters = theme_data_manager.replace_parameter_keywords(enhance.parameters  ) #Replace keywords in parameters
            _enh_out_filename = settings.TMP_FILE_PATH + name_part +'_' + file_prefix + '_enh'+str(i)+ ext_part #name file as filename_enh1.ext etc.
            _params = settings.ENHANCEMENT_SCRIPT_DIR + enhance.script_path +' '
            if _enhancement_parameters: #append parameters if exists
                _params += _enhancement_parameters
                _params += ' '
            _params += _tmp_filename
            _params += ' '
            _params += _enh_out_filename
            subprocess.call(_params, shell=True, env=os.environ.copy()) #like ./script parameters input_file output_file
            if i > 0: #Delete file if it is not the very first downloaded raw data
                os.remove(_tmp_filename)
            _tmp_filename = _enh_out_filename
        Log.debug('_tmp_filename1:' + _tmp_filename)
        _current_filename =  _tmp_filename.replace(settings.TMP_FILE_PATH, settings.ENHANCED_FILE_PATH)
        _save_filename = settings.SAVE_PREFIX + _current_filename
        Log.debug('_tmp_filename2 :' + _tmp_filename)
        Log.debug('_save_filename :' + _save_filename)
        Log.debug('_current_filename :' + _current_filename)

        shutil.move(_tmp_filename, _save_filename)
        return _current_filename
