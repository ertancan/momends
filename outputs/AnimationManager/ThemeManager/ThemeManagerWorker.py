__author__ = 'ertan'
from Outputs.AnimationManager.models import ThemeData,ImageEnhancementGroup,Theme
from Outputs.AnimationManager.ImageEnhancementUtility.ImageEnhancementUtilityWorker import ImageEnhancementUtility
from Outputs.AnimationManager.ThemeManager.ThemeDataManager import ThemeDataManager
class ThemeManagerWorker:

    def __init__(self,theme):
        self.theme = theme
        self.enhancement_applied_objects = dict()
        self.data_manager = ThemeDataManager(theme)

    def apply_theme(self, outdata,file_prefix):
        """
        :param out: OutData to apply the theme enhancements and fill with theme data
        :return: outData filled with theme data and enhanced images
        """
        filled_data = self._fill_theme_data(outdata)
        enhanced_data = self._apply_image_enhancement(filled_data,file_prefix)
        enhanced_data.save()
        return enhanced_data


    def _fill_theme_data(self, outdata):
        keywords = ThemeData.THEME_DATA_TYPE_KEYWORDS
        used_type = outdata.animation.used_object_type
        if used_type in keywords:
            index = keywords.index(used_type)
            obj_type = index/3
            request_type = index % 3 # 0 getPrevious, 1 getNext, 2 getRand
            print 'object type:'+str(obj_type)+' request type:'+str(request_type)
            if request_type == 0:
                print 'getting previous'
                theme_data = self.data_manager.getPreviousData(obj_type)
            elif request_type == 1:
                theme_data = self.data_manager.getNextData(obj_type)
            else:
                theme_data = self.data_manager.getRandData(obj_type)
            outdata.final_data_path = theme_data.data_path
            outdata.selection_criteria = 'Theme Asset'
        return  outdata


    def _apply_image_enhancement(self, outdata, file_prefix):
        """
        Applies one of the theme enhancements randomly to the given outdata if it is user photo
        :param outdata: OutData that contains photo
        :param file_prefix: to be used while naming the output
        :return: outData
        """
        photo_keywords = ['{{USER_PHOTO}}','{{NEXT_USER_PHOTO}}','{{RAND_USER_PHOTO}}']
        data_type = outdata.animation.used_object_type #Check if we need to apply enhancement on this data
        if not data_type in photo_keywords:
            return outdata

        rand_enhancement = self.theme.image_enhancement_groups.order_by('?')[0]
        if not rand_enhancement: #Check if there is a theme enhancement, set final data to raw data otherwise
            outdata.final_data_path = outdata.raw.data
            outdata.save()
            return outdata

        raw_filename= outdata.raw.data
        if raw_filename in self.enhancement_applied_objects: #Don't apply enhancement on the same object twice
            print 'Image already enhanced'
            outdata.final_data_path = self.enhancement_applied_objects[raw_filename]
            outdata.save()
            return outdata

        last_filename = ImageEnhancementUtility.applyThemeEnhancementsOnImage(raw_filename,rand_enhancement.image_enhancement_functions,file_prefix)

        outdata.final_data_path = last_filename #Update final data with enhanced one
        self.enhancement_applied_objects[raw_filename] = last_filename

        return outdata
