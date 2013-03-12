__author__ = 'ertan'
from Outputs.AnimationManager.models import ThemeData, AppliedPostEnhancement, PostEnhancement
from DataManager.models import RawData
from DataManager.DataManagerUtil import DataManagerUtil
from Outputs.AnimationManager.ImageEnhancementUtility.ImageEnhancementUtilityWorker import ImageEnhancementUtility
from Outputs.AnimationManager.models import CoreAnimationData
from Outputs.AnimationManager.ThemeManager.ThemeDataManager import ThemeDataManager
from LogManagers.Log import Log
from django.conf import settings


class ThemeManagerWorker:

    def __init__(self, theme):
        self.theme = theme
        self.enhancement_applied_objects = dict()
        self.data_manager = ThemeDataManager(theme)

    def apply_theme(self, outdata, file_prefix):
        """
        :param out: OutData to apply the theme enhancements and fill with theme data
        :return: outData filled with theme data and enhanced images
        """
        filled_data = self._fill_theme_data(outdata)
        enhanced_data = self._apply_image_enhancement(filled_data, file_prefix)
        enhanced_data_with_post_enh = self._set_post_enhancements(enhanced_data)
        enhanced_data_with_post_enh.save()
        return enhanced_data_with_post_enh

    def _fill_theme_data(self, outdata):
        _used_theme_data = outdata.animation.used_theme_data
        if _used_theme_data:
            outdata.final_data_path = _used_theme_data.data_path
            outdata.parameters = _used_theme_data.parameters
            outdata.selection_criteria = 'Theme Asset'
            return outdata
        used_type = outdata.animation.used_object_type
        if used_type:
            theme_data = self.data_manager.get_data_for_keyword(used_type)
            if theme_data:
                outdata.final_data_path = theme_data.data_path
                outdata.parameters = theme_data.parameters
                outdata.selection_criteria = 'Theme Asset'
        return outdata

    def _apply_image_enhancement(self, outdata, file_prefix):
        """
        Applies one of the theme enhancements randomly to the given outdata if it is user photo
        :param outdata: OutData that contains photo
        :param file_prefix: to be used while naming the output
        :return: outData
        """
        photo_keywords = ['{{USER_PHOTO}}', '{{NEXT_USER_PHOTO}}', '{{RAND_USER_PHOTO}}']
        data_type = outdata.animation.used_object_type  # Check if we need to apply enhancement on this data
        if not data_type in photo_keywords:
            return outdata

        _raw = outdata.raw
        if not _raw.data:  # Download photo if not downloaded already
            Log.debug('Downloading :'+str(_raw))
            _raw.data = DataManagerUtil.download_raw_data(_raw)
            _raw.save()

        rand_enhancement = self.theme.enhancement_groups.filter(post_enhancement=False).filter(applicable_to=RawData.DATA_TYPE['Photo']).order_by('?')[0]
        if not rand_enhancement:  # Check if there is a theme enhancement, set final data to raw data otherwise
            outdata.final_data_path = outdata.raw.data
            return outdata

        raw_filename = outdata.raw.data

        if raw_filename in self.enhancement_applied_objects:  # Don't apply enhancement on the same object twice
            Log.debug('Image already enhanced')
            outdata.final_data_path = self.enhancement_applied_objects[raw_filename]
            outdata.save()
            return outdata

        last_filename = ImageEnhancementUtility.applyThemeEnhancementsOnImage(settings.SAVE_PREFIX + raw_filename,
                                                                              rand_enhancement.enhancement_functions, file_prefix, self.data_manager)

        outdata.final_data_path = last_filename  # Update final data with enhanced one
        self.enhancement_applied_objects[raw_filename] = last_filename

        return outdata

    def _set_post_enhancements(self, outdata):
        """
        Selects a random post enhancement for the given data, creates a new entry in AppliedPostEnhancements table.
        !! Parameters of 'PostEnhancement' object overrides parameters of 'ThemeData' !!
        :param outdata: OutData object that will receive post enhancement
        :return: same outdata object
        """
        if not outdata.raw:
            return outdata
        used_obj = outdata.animation.used_object_type
        if used_obj in CoreAnimationData.SPECIAL_DATA_KEYWORDS:  # Special objects (i.e. title)
            index = CoreAnimationData.SPECIAL_DATA_KEYWORDS.index(used_obj)
            if index == 0:  # Title
                rand_enhancement = self.theme.enhancement_groups.filter(post_enhancement=True).filter(applicable_to=RawData.DATA_TYPE['Status']).order_by('?')  # Behave like status
            else:
                return outdata
        else:  # Regular objects
            index = CoreAnimationData.USER_DATA_KEYWORDS.index(used_obj)
            if index % 3 == 0:  # Post enhancement already applied, since it is not NEXT_OBJECT
                return outdata
            rand_enhancement = self.theme.enhancement_groups.filter(post_enhancement=True).filter(applicable_to=outdata.raw.type).order_by('?')

        if len(rand_enhancement) == 0:
            return outdata

        rand_enhancement = rand_enhancement[0]
        items = rand_enhancement.enhancement_functions
        if not items and len(items) == 0:
            return outdata

        post_enh_funcs = items.split(',')
        for func in post_enh_funcs:
            next_enh = PostEnhancement.objects.get(pk=func)
            applied_enh = AppliedPostEnhancement()
            applied_enh.outdata = outdata
            applied_enh.type = next_enh.type
            enh_parameter = next_enh.parameters
            if next_enh.filepath:
                applied_enh.filepath = next_enh.filepath
            elif next_enh.used_object_type:
                theme_data = self.data_manager.get_data_for_keyword(next_enh.used_object_type)
                applied_enh.filepath = theme_data.data_path
                if not enh_parameter or len(enh_parameter) == 0:  # Override theme_data's parameters here
                    enh_parameter = theme_data.parameters

            enh_parameter = self.data_manager.replace_parameter_keywords(enh_parameter)  # Replace used keywords like {{THEME_DATA_PARAMETER}} here
            applied_enh.parameters = enh_parameter
            applied_enh.save()

        return outdata
