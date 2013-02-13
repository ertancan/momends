__author__ = 'goktan'

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.views.generic.edit import FormView
from django.views.generic.base import TemplateView
from django.views.generic.base import View
from django.views.generic.base import RedirectView
from django.http import HttpResponse
from WebManager.forms import CreateMomendForm
from WebManager.forms import SettingsForm
from DataManager.DataManager import DataManager
from DataManager.models import Momend
from DataManager.models import DeletedMomend
from DataManager.models import RawData
from Outputs.AnimationManager.models import UserInteraction
from Outputs.AnimationManager.models import DeletedUserInteraction
from Outputs.AnimationManager.models import OutData
from Outputs.AnimationManager.models import AnimationPlayStat
from Outputs.AnimationManager.models import Theme
from DataManager.DataEnrich.EnrichDataWorker import EnrichDataWorker
from social_auth.db.django_models import UserSocialAuth
from random import randint
from django.core.exceptions import ObjectDoesNotExist
from LogManagers.Log import Log
from django.utils import simplejson
from django.contrib import messages
from django.core.files.uploadedfile import UploadedFile
from sorl.thumbnail import get_thumbnail
from DataManager.DataManagerUtil import DataManagerUtil
from django.conf import settings

class HomePageLoggedFormView(FormView):
    form_class = CreateMomendForm
    template_name = 'HomePageTemplate.html'
    def get_context_data(self, **kwargs):
        context =  super(HomePageLoggedFormView,self).get_context_data(**kwargs)
        context['user_top_momends'] = EnrichDataWorker.get_top_user_momends(user=self.request.user, max_count=10)
        context['public_top_momends'] = EnrichDataWorker.get_top_public_momends(max_count=20)
        return context


    def form_valid(self, form):
        Log.debug('Create momend form sent form')
        _momend_name = form.cleaned_data['momend_name']
        _start_date = form.cleaned_data['start_date']
        _finish_date = form.cleaned_data['finish_date']
        _privacy = form.cleaned_data['privacy_type']
        _user = User.objects.get(username=self.request.user)
        dm = DataManager(_user)
        try:
            _args = dict()
            _args['is_date'] = True
            _args['since'] = _start_date
            _args['until'] = _finish_date
            momend_id = dm.create_momend(name=_momend_name, duration=30, privacy=_privacy,
                theme=Theme.objects.get(pk=form.cleaned_data['momend_theme']), **_args)
        except NotImplementedError as e:
            Log.error('Error while creating the momend: '+str(e))
            messages.error(self.request, 'Error while creating the momend')
            self.success_url = reverse('momends:home-screen' ) #Redirect back to home screen in case of exception
            return super(HomePageLoggedFormView,self).form_valid(form)

        status = dm.get_last_status()
        has_data = False
        for key,value in status.iteritems():
            if status[key] == 'Success':
                has_data = True
                break
        if not has_data:
            messages.warning(self.request, 'Could not collect any data')
            self.success_url = reverse('momends:home-screen' )
        else: #Collected some data and created momend, append status and redirect to show page
            messages.info(self.request, status)
            self.success_url = reverse('momends:show-momend', args = ('m', momend_id,) )
        return super(HomePageLoggedFormView,self).form_valid(form)

class HomePageNotLoggedView(TemplateView):
    template_name = 'HomePageTemplate.html'
    def get_context_data(self, *args, **kwargs):
        if randint(0,1) == 0:
            self.template_name = 'BasicMainPageTemplate.html' #basic random selection for main page! just for fun
        context = super(HomePageNotLoggedView, self).get_context_data(**kwargs)
        context['public_top_momends'] = EnrichDataWorker.get_top_public_momends(max_count=20)
        return context

class MomendPlayerView(TemplateView):
    template_name = 'MomendPlayerTemplate.html'

class ShowMomendView(TemplateView):
    template_name = 'ShowMomendTemplate.html'

    def dispatch(self, request, *args, **kwargs):
        play_stat = AnimationPlayStat()
        if kwargs['type'] == 'm': #Whether it is momend or interaction
            play_stat.momend_id = kwargs['id']
        elif kwargs['type'] == 'i':
            play_stat.interaction_id = kwargs['id']

        if 'HTTP_REFERER' in request.META:
            play_stat.redirect_url = request.META['HTTP_REFERER']
        else:
            play_stat.redirect_url = 'Direct'
        if not request.user.is_anonymous():
            play_stat.user = request.user
        play_stat.save()

        return super(ShowMomendView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(ShowMomendView, self).get_context_data(**kwargs)
        if kwargs['type'] == 'm':
            _momend = Momend.objects.get(pk = kwargs['id'])
        elif kwargs['type'] == 'i':
            _momend = UserInteraction.objects.get(pk = kwargs['id']).momend
        else:
            context['error'] = 1
            return context

        context['error']  = '0'
        context['momend'] = _momend
        context['interactions'] = UserInteraction.objects.filter(momend = _momend)
        context['related_momends'] = EnrichDataWorker.get_related_momends(momend=_momend, max_count=10, get_private=True)
        _all_dis = OutData.objects.filter(owner_layer__momend=_momend).values('raw').distinct()
        _icons = ['icon-picture', 'icon-comment', 'icon-pushpin', 'icon-desktop', ' icon-music']
        _used_media = []
        for _out_data in _all_dis:
            if _out_data['raw']:
                _obj = RawData.objects.get(pk=_out_data['raw'])
                _tmp = dict()
                _tmp['data'] = _obj.data
                _tmp['thumb'] = _obj.thumbnail
                _tmp['original_id'] = _obj.original_id
                _tmp['provider'] = _obj.provider.name.lower()
                _tmp['type'] = RawData.DATA_TYPE.keys()[_obj.type].lower()
                _tmp['type_icon'] = _icons[_obj.type]
                _tmp['original_path'] = _obj.original_path
                _used_media.append(_tmp)
        context['used_media'] = _used_media
        return context

class GetMomendView(TemplateView):
    template_name = 'GetMomendTemplate.html'

    def get_context_data(self, **kwargs):
        context = super(GetMomendView, self).get_context_data(**kwargs)
        try:
            if kwargs['type'] == 'm':
                obj = Momend.objects.get(pk = kwargs['id'])
                if obj.privacy == Momend.PRIVACY_CHOICES['Private']:
                    if obj.owner != self.request.user:
                        context['momend'] = '{"error":"not authorised"}'
                        return context
                context['momend'] = obj.toJSON()
            elif kwargs['type'] =='i':
                obj = UserInteraction.objects.get(pk = kwargs['id'])
                if obj.momend.privacy == Momend.PRIVACY_CHOICES['Private']:
                    if obj.momend.owner != self.request.user:
                        context['momend'] = '{"error":"not authorised"}'
                        return context
                context['momend'] = obj.toJSON()
            else:
                context['momend'] = '{"error":"bad request"}'
        except ObjectDoesNotExist:
            context['momend'] = '{"error":"bad request"}'
        return context

class SaveInteractionView(View):
    def post(self, request, *args, **kwargs):
        if not request.user:
            return _generate_json_response(False, 'Not authenticated save interaction request', 'Please Login First')
        try:
            queue = request.POST['queue']
            momend_id = request.POST['id']
            interaction = UserInteraction()
            interaction.momend_id = momend_id
            interaction.interaction = queue
            interaction.creator = request.user
            interaction.save()
            return _generate_json_response(True, 'Interaction Saved', url=str(reverse_lazy('momends:show-momend',args=('i',interaction.pk))))
        except Exception as e:
            return _generate_json_response(False, 'Error while saving interaction: '+str(e), 'Try Again')

class DeleteMomendView(View):
    def get(self, request, *args, **kwargs):
        if not request.user:
            return _generate_json_response(False, 'Not authenticated delete request', 'Please Login First')
        if kwargs['type'] == 'm':
            try:
                momend = Momend.objects.get(pk = kwargs['id'])
                if not momend.owner == request.user:
                    Log.warn("Trying to delete someone else's momend")
                    return _generate_json_response(False, user_msg='You cannot delete this momend')

                stat_obj = DeletedMomend()
                stat_obj.set_momend_data(momend)
                stat_obj.save()

                for interaction in momend.userinteraction_set.all():
                    interaction_stat = DeletedUserInteraction()
                    interaction_stat.set_interaction_data(interaction)
                    interaction_stat.momend_owner_deleted = True
                    interaction_stat.save()

                momend.delete()
                return _generate_json_response(True)
            except Exception as e:
                return _generate_json_response(False, 'Cannot delete momend: '+str(e), 'Try Again')

        if kwargs['type'] == 'i':
            try:
                interaction = UserInteraction.objects.get(pk = kwargs['id'])
                if not interaction.creator == request.user and not interaction.momend.owner == request.user:
                    Log.warn("Trying to delete someone else's interaction")
                    return _generate_json_response(False, user_msg='You cannot delete this interaction')

                interaction_stat = DeletedUserInteraction()
                interaction_stat.set_interaction_data(interaction)
                interaction_stat.momend_owner_deleted = request.user == interaction.momend.owner
                interaction_stat.save()

                interaction.delete()

                return _generate_json_response(True)
            except Exception as e:
                return _generate_json_response(False, 'Cannot delete interaction: '+str(e), 'Try Again')



class SettingsFormView(FormView):
    form_class = SettingsForm
    template_name = 'SettingsTemplate.html'
    success_url = reverse_lazy('momends:home-screen')
    def get_context_data(self, **kwargs):
        context =  super(SettingsFormView,self).get_context_data(**kwargs)
        providers = UserSocialAuth.objects.filter(user=self.request.user)
        context['providers'] = [pr.provider for pr in providers]
        return context

class MainRedirectView(RedirectView):
        def get_redirect_url(self):
            if self.request.user.is_authenticated():
                url = reverse('momends:home-screen')
            else:
                url = reverse('momends:main-screen')
            return url


class UserProfileTemplateView(TemplateView):
    template_name = 'UserProfileTemplate.html'
    def get_context_data(self, **kwargs):
        context = super(UserProfileTemplateView, self).get_context_data(**kwargs)
        try:
            _user = User.objects.get(pk = kwargs['id'])
            _obj = UserSocialAuth.objects.filter(user = kwargs['id']) #TODO put here more
        except KeyError:
            _user = User.objects.get(username = kwargs['username'])
        context['user_top_momends'] = EnrichDataWorker.get_top_user_momends(user=_user, max_count=20, get_private=False)
        context['profile_user'] = _user
        return context


class FileUploadView(View):
    def post(self, request, *args, **kwargs):
        if request.FILES == None:
            return _generate_json_response(False, 'Must have files attached: ', 'Try Again')
        file = request.FILES[u'files[]']
        wrapped_file = UploadedFile(file)
        filename = wrapped_file.name
        file_size = wrapped_file.file.size
        Log.debug ('Got file: "%s"' % str(filename))
        Log.debug('Content type: "$s" % file.content_type')

        #writing file manually into model
        #because we don't need form of any type.
        _raw = RawData()
        _raw.original_id = RawData.key_generate
        _raw.owner = request.user
        _raw.provider = 'Upload' #TODO change here
        _raw.title =  str(filename)
        _raw.data = DataManagerUtil.create_file(file, str(_raw))

        _raw.type = RawData.DATA_TYPE['Photo']

        #getting thumbnail url using sorl-thumbnail
        if 'image' in file.content_type.lower():
            _raw.thumbnail = DataManagerUtil.create_photo_thumbnail(settings.SAVE_PREFIX + _raw.data, str(_raw)+ '_thumb'+ 'jpg')

        _raw.save()
        Log.debug('Uploaded file saving done')
        #settings imports
        try:
            #file_delete_url = settings.MULTI_FILE_DELETE_URL+'/'
            file_url = ""#settings.MULTI_IMAGE_URL+'/'+image.key_data+'/'
        except AttributeError:
            file_delete_url = 'multi_delete/'
            file_url = ""#'multi_image/'+image.key_data+'/'
            #generating json response array
        result = {
            'files': [ {"name":filename,
                        "size":file_size,
                        "url":file_url,
                        "thumbnail_url":_raw.thumbnail,
                        "delete_url":'',
                        "delete_type":"POST",}
            ]
        }
        response_data = simplejson.dumps(result)

        #checking for json data type
        #big thanks to Guy Shapiro
        if "application/json" in request.META['HTTP_ACCEPT_ENCODING']:
            mimetype = 'application/json'
        else:
            mimetype = 'text/plain'
        return HttpResponse(response_data, mimetype=mimetype)

def _generate_json_response(success, log_message=None, user_msg=None, **kwargs):
    if log_message:
        if success:
            Log.info(log_message)
        else:
            Log.error(log_message)

    _response = dict()
    _response['resp'] = success
    _response['message'] = user_msg
    for key, value in kwargs.iteritems():
        _response[key] = value
    json = simplejson.dumps(_response)
    return HttpResponse(json)