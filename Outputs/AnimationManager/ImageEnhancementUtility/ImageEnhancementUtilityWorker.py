__author__ = 'ertan'
from django.conf import settings
import subprocess,os
import re
from Outputs.AnimationManager.models import ImageEnhancement
from Outputs.AnimationManager.models import ThemeData
from DataManager.DataManagerUtil import DataManagerUtil

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

        current_filename = filename
        try:
            dot_index = filename.rindex('.')
            name_part = filename[:dot_index]
            ext_part = filename[dot_index:]
        except ValueError:
            name_part = filename
            ext_part = ''  #there is no extension, unlikely but possible

        if settings.COLLECTED_FILE_PATH in name_part:
            name_part = name_part[len(settings.COLLECTED_FILE_PATH):]
        _enh_tmp_out_filename = None
        _enh_out_filename = None
        for i, enhance in enumerate(enhancement_objects):
            _enhancement_parameters = ImageEnhancementUtility._replace_parameter_keywords(enhance.parameters, theme_data_manager) #Replace keywords in parameters
            _enh_tmp_out_filename = settings.TMP_FILE_PATH + name_part +'_' + file_prefix + '_enh'+str(i)+ ext_part #name file as filename_enh1.ext etc.
            _enh_out_filename = settings.ENHANCED_FILE_PATH + name_part +'_' + file_prefix + '_enh'+str(i)+ ext_part #name file as filename_enh1.ext etc.
            params = settings.ENHANCEMENT_SCRIPT_DIR + enhance.script_path +' '
            params += _enhancement_parameters
            params += ' '
            params += current_filename
            params += ' '
            params += _enh_tmp_out_filename
            subprocess.call(params, shell=True, env=os.environ.copy()) #like ./script parameters input_file output_file
            if i > 0: #Delete file if it is not the very first downloaded raw data
                os.remove(current_filename)
            current_filename = _enh_tmp_out_filename

        if _enh_out_filename:
            DataManagerUtil.move_for_serving(_enh_tmp_out_filename, _enh_out_filename)
        return _enh_out_filename

    @staticmethod
    def _replace_parameter_keywords(parameter,theme_data_manager):
        """
        Replaces occurrences of reserved keywords such as {{THEME_FRAME}} or {{THEME_DATA_PARAMETER}}
        :param parameter: parameter string of enhancement
        :param theme_data_manager: ThemeDataManager object
        :return: replaced parameter string
        """
        if not parameter:
            return None
        keyword_re='(\\{\\{(?:[a-z][a-z0-9_]*)\\}\\})'
        keyword_finder = re.compile(keyword_re,re.IGNORECASE|re.DOTALL)

        regex_result =keyword_finder.search(parameter)
        while regex_result:
            matched_keyword = regex_result.group()
            theme_data = theme_data_manager.get_theme_data_for_keyword(matched_keyword)
            if theme_data:
                parameter = parameter.replace(matched_keyword,theme_data.data_path)
            elif matched_keyword == ThemeData.THEME_DATA_PARAMETER_KEYWORD:
                parameter = parameter.replace(matched_keyword, theme_data_manager.getLastResult().parameters)

            regex_result =keyword_finder.search(parameter)

        return parameter
