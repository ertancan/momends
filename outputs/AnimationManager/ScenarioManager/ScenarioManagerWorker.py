__author__ = 'ertan'
from DataManager.models import AnimationLayer,OutData
from Outputs.AnimationManager.models import AnimationGroup,Scenario,CoreAnimationData
class ScenarioManagerWorker(object):
    def prepare_scenario(self, momend, duration, theme, scenario=None, selection='basic', max_photo=0, max_bg=0, max_status=0, max_checkin=0):
        """Currently first 3 levels are assigned; 0-Background Layer, 1-Foreground Layer, 2-Music Layer. You can use any layer and
        any other layer as you wish. I believed these can make inter-layer communication a bit easier, e.g., You can wait until music changes
        by waiting the 2nd layer or wait until background change animation to disappear by waiting layer 0.
        I may introduce breakpoint broadcasting soon.
        :param duration: Approximate duration of the output animation
        :param theme: Theme to be used in animation
        :param scenario: If the scenario is known, None if it will be chosen randomly
        :param selection: Indicates which selection method (i.e., 'basic', 'random') will be used while selecting animation groups,
        :param max_photo: Max number of photos, default=None, any number
        :param max_bg: Max number of background photos, default=None, any number
        :param max_status: Max number of status updates, default=None, any number
        :param max_checkin: Max number of checkins, default=None, any number
        :return: Dictionary{'layers':List<AnimationLayer>,'objects':List<AnimationObject>}, duration, used_bg_count, used_photo_count, used_status_count, used_checkin_count
        """

        if not scenario:
            scenario = Scenario.objects.filter(compatible_themes=theme).order_by('?')[0]

        compatible_animation_groups = AnimationGroup.objects.filter(scenario=scenario)

        if selection == 'random':
            compatible_animation_groups.order_by('?')

        bgLayer = AnimationLayer()
        bgLayer.description = 'Background Layer'
        bgLayer.layer = 0
        bgLayer.momend = momend
        bgLayer.save()
        used_bg_groups = []

        frontLayer = AnimationLayer()
        frontLayer.description = 'Main Layer'
        frontLayer.layer = 1
        frontLayer.momend = momend
        frontLayer.save()
        used_front_groups = []

        musicLayer = AnimationLayer()
        musicLayer.description = 'Music Layer'
        musicLayer.layer = 2
        musicLayer.momend = momend
        musicLayer.save()
        used_music_groups = []


        bgGroup = compatible_animation_groups.filter(type=AnimationGroup.ANIMATION_GROUP_TYPE['Background'])
        frontGroup = compatible_animation_groups.filter(type=AnimationGroup.ANIMATION_GROUP_TYPE['Normal']) #TODO use screen change,too
        musicGroup = compatible_animation_groups.filter(type=AnimationGroup.ANIMATION_GROUP_TYPE['Music'])

        used_photo = 0
        used_status = 0
        used_bg = 0
        used_checkin = 0

        bg_duration = 0
        front_duration = 0
        music_duration = 0

        #Greedy choice below
        for bgAnim in bgGroup:
            if bgAnim.duration + bg_duration <= duration:
                if used_bg + bgAnim.needed_bg <= max_bg:
                    used_bg += bgAnim.needed_bg
                    bg_duration += bgAnim.duration
                    used_bg_groups.append(bgAnim)

                if bg_duration == duration:
                    break

        for anim in frontGroup:
            if front_duration + anim.duration <= duration:
                if used_photo + anim.needed_photo <= max_photo and used_checkin + anim.needed_location <= max_checkin and used_status + anim.needed_status <= max_status:
                    used_photo += anim.needed_photo
                    used_checkin += anim.needed_location
                    used_status += anim.needed_status
                    front_duration += anim.duration
                    used_front_groups.append(anim)

                if front_duration == duration:
                    break

        for musicAnim in musicGroup:
            if music_duration + musicAnim.duration <= duration:
                used_music_groups.append(musicAnim)
                music_duration += musicAnim.duration

        #Generate output
        out_layers = [bgLayer, frontLayer, musicLayer]
        out = {'layers':out_layers,
               'objects':self._generate_outdata_from_groups(theme,out_layers,[used_bg_groups,used_front_groups,used_music_groups])}
        return out, front_duration, used_bg, used_photo, used_status, used_checkin

    def _generate_outdata_from_groups(self,theme,layers,group_layers):
        """
        :param theme: That was used while selecting the scenario objects
        :param layers: AnimationLayer list which were created for this momend
        :param group_layers: layers of AnimationGroup objects to be used for instantiating OutData
        :return: List - same number of layers with 'layers' list - that contains OutData objects for the momend
        """
        assert len(layers) == len(group_layers)
        result = []
        for i in range(0,len(layers)): #For every layer of data
            result.append([])
            for group in group_layers[i]: #For every AnimationGroup in layers
                group_objects = CoreAnimationData.objects.filter(group=group)
                for obj in group_objects: #For every CoreAnimation in each AnimationGroup
                    outData = OutData()
                    outData.owner_layer = layers[i]
                    outData.animation = obj
                    outData.theme = theme
                    result[i].append(outData)

        return result
