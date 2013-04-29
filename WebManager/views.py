from django.core.mail import EmailMultiAlternatives
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.views.generic.edit import FormView
from django.views.generic.base import TemplateView
from django.views.generic.base import View
from django.views.generic.base import RedirectView
from django.http import HttpResponse
from WebManager.forms import SettingsForm
from WebManager.forms import DocumentForm
from DataManager.DataManager import DataManager
from DataManager.models import Momend
from DataManager.models import DeletedMomend
from DataManager.models import RawData
from DataManager.models import MomendStatus
from DataManager.models import encode_id, decode_id
from DataManager.models import Provider
from Outputs.AnimationManager.models import UserInteraction
from Outputs.AnimationManager.models import DeletedUserInteraction
from Outputs.AnimationManager.models import OutData
from Outputs.AnimationManager.models import AnimationPlayStat
from Outputs.AnimationManager.models import Theme
from DataManager.DataEnrich.DataEnrichManager import DataEnrichManager
from social_auth.db.django_models import UserSocialAuth
from datetime import datetime
import pytz
from LogManagers.Log import Log
from django.utils import simplejson
from django.core.files.uploadedfile import UploadedFile
from DataManager.DataManagerUtil import DataManagerUtil
from django.conf import settings
import traceback
import json

ERROR_TYPES = {'WRONG_PARAMETER': 0,
               'MISSING_PARAMETER': 1,
               'NOT_FOUND': 2,
               }


class HomePageLoggedFormView(TemplateView):
    template_name = 'BasicMainPageTemplate.html'

    def get_context_data(self, **kwargs):
        context = super(HomePageLoggedFormView, self).get_context_data(**kwargs)
        context['user'] = self.request.user
        context['user_top_momends'] = DataEnrichManager.get_top_user_momends(user=self.request.user, max_count=10)
        context['public_top_momends'] = DataEnrichManager.get_top_public_momends(max_count=20)
        context['should_create_automatically'] = False
        providers = UserSocialAuth.objects.filter(user=self.request.user)
        context['providers'] = [pr.provider for pr in providers]
        context['home'] = True
        return context


class HomePageNotLoggedView(TemplateView):
    template_name = 'BasicMainPageTemplate.html'

    def get_context_data(self, *args, **kwargs):
        context = super(HomePageNotLoggedView, self).get_context_data(**kwargs)
        context['public_top_momends'] = DataEnrichManager.get_top_public_momends(max_count=20)
        context['should_create_automatically'] = False
        return context


class MomendPlayerView(TemplateView):
    template_name = 'MomendPlayerTemplate.html'

    def get_context_data(self, *args, **kwargs):
        context = super(MomendPlayerView, self).get_context_data(**kwargs)
        decoded_id = decode_id(kwargs['id'])
        _momend = None
        if decoded_id:
            try:
                if kwargs['type'] == 'm':
                    _momend = Momend.objects.get(pk=decoded_id)
                elif kwargs['type'] == 'i':
                    _momend = UserInteraction.objects.get(pk=decoded_id).momend
                else:
                    context['error'] = ERROR_TYPES['WRONG_PARAMETER']
                    return context
            except ObjectDoesNotExist:
                context['error'] = ERROR_TYPES['NOT_FOUND']
        else:
            context['error'] = ERROR_TYPES['WRONG_PARAMETER']
            return context
        context['error'] = 0
        context['momend'] = _momend
        return context


class ShowMomendView(TemplateView):
    template_name = 'BasicMainPageTemplate.html'

    def dispatch(self, request, *args, **kwargs):
        decoded_id = decode_id(kwargs['id'])
        if decoded_id:
            play_stat = AnimationPlayStat()

            if kwargs['type'] == 'm':  # Whether it is momend or interaction
                play_stat.momend_id = decoded_id
            elif kwargs['type'] == 'i':
                play_stat.interaction_id = decoded_id

            if 'HTTP_REFERER' in request.META:
                play_stat.redirect_url = request.META['HTTP_REFERER']
            else:
                play_stat.redirect_url = 'Direct'
            if not request.user.is_anonymous():
                play_stat.user = request.user
            try:
                play_stat.save()
            except IntegrityError:
                Log.debug('Trying to view nonexistent momend, so not saving play stat')

        return super(ShowMomendView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(ShowMomendView, self).get_context_data(**kwargs)

        if not self.request.user.is_anonymous():  # Put authentication details even if momend is not exists!
            providers = UserSocialAuth.objects.filter(user=self.request.user)
            context['providers'] = [pr.provider for pr in providers]

        decoded_id = decode_id(kwargs['id'])
        if decoded_id:  # Show only if id is valid
            try:
                if kwargs['type'] == 'm':
                    _momend = Momend.objects.get(pk=decoded_id)
                elif kwargs['type'] == 'i':
                    _momend = UserInteraction.objects.get(pk=decoded_id).momend
                else:
                    context['error'] = ERROR_TYPES['WRONG_PARAMETER']
                    return context
            except ObjectDoesNotExist:
                Log.warn('Momend or interaction does not exists:('+kwargs['type']+'-'+str(decoded_id))  # TODO change to debug after introducing delete
                context['error'] = ERROR_TYPES['NOT_FOUND']
                return context

            context['error'] = '0'
            context['momend'] = _momend
            context['interactions'] = UserInteraction.objects.filter(momend=_momend)
            context['related_momends'] = DataEnrichManager.get_related_momends(momend=_momend, max_count=10, get_private=True)

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
        else:  # If id is wrong (decoded_id is none)
            context['error'] = ERROR_TYPES['WRONG_PARAMETER']
        return context


class GetMomendView(TemplateView):
    template_name = 'GetMomendTemplate.html'

    def get_context_data(self, **kwargs):
        context = super(GetMomendView, self).get_context_data(**kwargs)
        decoded_id = decode_id(kwargs['id'])
        if not decoded_id:
            context['momend'] = '{"error":"invalid momend id"}'
            return context
        try:
            if kwargs['type'] == 'm':
                obj = Momend.objects.get(pk=decoded_id)
                if obj.privacy == Momend.PRIVACY_CHOICES['Private']:
                    if obj.owner != self.request.user:
                        context['momend'] = '{"error":"not authorized"}'
                        return context
                context['momend'] = obj.toJSON()
            elif kwargs['type'] == 'i':
                obj = UserInteraction.objects.get(pk=decoded_id)
                if obj.momend.privacy == Momend.PRIVACY_CHOICES['Private']:
                    if obj.momend.owner != self.request.user:
                        context['momend'] = '{"error":"not authorized"}'
                        return context
                context['momend'] = obj.toJSON()
            else:
                context['momend'] = '{"error":"bad request"}'
        except ObjectDoesNotExist:
            context['momend'] = '{"error":"bad request"}'
        return context


class SaveInteractionView(View):
    def post(self, request, *args, **kwargs):
        try:
            queue = request.POST['queue']
            encoded_id = request.POST['id']
            momend_id = decode_id(encoded_id)
            interaction = UserInteraction()
            interaction.momend_id = momend_id
            interaction.interaction = queue
            interaction.creator = request.user
            interaction.save()
            interaction.cryptic_id = encode_id(interaction.id)
            interaction.save()
            return _generate_json_response(True, 'Interaction Saved', url=str(reverse_lazy('momends:show-momend', args=('i', interaction.cryptic_id))))
        except Exception as e:
            return _generate_json_response(False, 'Error while saving interaction: '+str(e), 'Try Again')


class SendAnimationAsMail(View):
    def post(self, request, *args, **kwargs):
        try:
            _type = request.POST['type']
            _cryptic_id = request.POST['cid']
            _email = request.POST['email']
        except:
            return _generate_json_response(False, 'Missing argument on share mail', 'Missing argument')
        _url = reverse('momends:show-momend', args=(_type, _cryptic_id,))
        if DataManagerUtil.send_share_email(self.request.user, _email.split(','), _url):
            return _generate_json_response(True, 'Send mail success')
        return _generate_json_response(False, user_msg='Send mail failed. Please try again!')  # Error logged on the send mail side


class GetUserFriendsView(View):
    """
    Return list of objects containing friendlist of current user.
    Response is in this format;
        [
            {
                name: Provider Name,
                local: [Data returned from provider worker]  # Named as local to be directly compatible with typeahead.js
            }
        ]
    """
    def get(self, request, *args, **kwargs):
        response = []
        providers = UserSocialAuth.objects.filter(user=request.user)
        for provider in providers:
            try:
                provider_response = dict()
                provider_response['name'] = provider.provider
                momends_provider = Provider.objects.get(name=provider.provider)
                provider_instance = momends_provider.instantiate_provider_worker()
                provider_response['local'] = provider_instance.get_friendlist(request.user)
                response.append(provider_response)
            except:
                Log.error('Get friendlist error')
                Log.error(traceback.format_exc())
        return _generate_json_response(True, 'Returning friendlist successfully', list=response)


class CreateMomendView(View):
    def post(self, request, *args, **kwargs):
        try:
            Log.debug('Create momend request: '+str(request.POST))
            _owner = request.user
            if 'owner' in request.POST:
                if request.user.is_superuser:
                    _owner = User.objects.get(pk=request.POST['owner'])
            _momend_name = request.POST['momend_name']
            _privacy = request.POST['privacy_type']

            _theme = request.POST['momend_theme']
            _theme = 1  # TODO remove after showing theme selection combo

            _send_mail = request.POST.get('mail', True)  # Send mail after create, default True
            dm = DataManager(_owner)
            try:
                _args = dict()
                if 'selected' in request.POST and request.POST['selected']:
                    _args['is_date'] = False
                    _args['selected'] = json.loads(request.POST['selected'])
                else:
                    _args['is_date'] = True
                    _args['selected'] = []
                    _args['since'] = datetime.strptime(request.POST['start_date'], '%d %b, %Y').replace(tzinfo=pytz.UTC)
                    _args['until'] = datetime.strptime(request.POST['finish_date'], '%d %b, %Y').replace(tzinfo=pytz.UTC)

                _create_params = request.POST.keys()
                for _param in _create_params:
                    if '-active' in _param:  # Provider disable requests
                        _args[_param] = request.POST[_param]

                if 'friends' in request.POST and len(request.POST['friends']) > 0:
                    _args['friends'] = request.POST['friends'].split(',')
                else:
                    _args['friends'] = []

                if 'chronological' in request.POST:
                    _args['chronological'] = request.POST['chronological']
                else:
                    _args['chronological'] = False

                _cryptic_id = dm.create_momend(name=_momend_name, duration=60, privacy=_privacy,
                                               theme=Theme.objects.get(pk=_theme), send_mail=_send_mail, **_args)
                if _cryptic_id:  # If created momend successfully
                    return _generate_json_response(True, 'Create momend request received', cid=_cryptic_id)
                _error_msg = dm.get_last_status()
                return _generate_json_response(False, 'Create momend failed with error message: '+str(_error_msg), _error_msg)
            except Exception as e:
                _log_critical_error('Exception while creating the momend', True, request.POST, request.user, traceback.format_exc())
                return _generate_json_response(False, 'Error while creating momend: '+str(e), 'An error occurred. Please try again')  # Could be any error
        except KeyError as e:
            Log.error(traceback.format_exc())
            return _generate_json_response(False, 'Error while creating momend: '+str(e), str(e))  # One of the parameters is missing
        except Exception as e:
            _log_critical_error('Impossible exception occurred while creating momend', True, request.POST, request.user, traceback.format_exc())
            return _generate_json_response(False, 'Error while creating momend (impossible): '+str(e), 'An error occurred. Please try again after a while')


class MomendStatusView(View):
    def get(self, request, *args, **kwargs):
        decoded_id = decode_id(kwargs['id'])
        if not decoded_id:
            return _generate_json_response(False, 'Invalid id on status', 'Invalid Id')
        try:
            Log.debug('Status for momend:'+str(decoded_id))
            _status_obj = MomendStatus.objects.get(momend_id=decoded_id)
            print _status_obj.status
            return _generate_json_response(True, user_msg=_status_obj.message, status=MomendStatus.MESSAGES[_status_obj.status])
        except Exception as e:
            return _generate_json_response(False, 'Exception on status check: '+str(e), 'Error while checking the status')


class DeleteMomendView(View):
    def get(self, request, *args, **kwargs):
        decoded_id = decode_id(kwargs['id'])
        if not decoded_id:
            return _generate_json_response(False, 'Invalid id on delete', 'Invalid Id')
        if kwargs['type'] == 'm':
            try:
                momend = Momend.objects.get(pk=decoded_id)
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
                interaction = UserInteraction.objects.get(pk=decoded_id)
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
        context = super(SettingsFormView, self).get_context_data(**kwargs)
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
            _user = User.objects.get(pk=kwargs['id'])
            _obj = UserSocialAuth.objects.filter(user=kwargs['id'])  # TODO put here more
        except KeyError:
            _user = User.objects.get(username=kwargs['username'])
        context['user_top_momends'] = DataEnrichManager.get_top_user_momends(user=_user, max_count=20, get_private=False)
        context['profile_user'] = _user
        return context


class UploadFormView(FormView):
    form_class = DocumentForm
    template_name = 'UploadTest.html'
    success_url = reverse_lazy('momends:home-screen')


class FileUploadView(View):
    def post(self, request, *args, **kwargs):
        if request.FILES is None:
            return _generate_json_response(False, 'Must have files attached: ', 'Try Again')
        _files = request.FILES[u'files[]']
        result = []
        for _file in _files:
            wrapped_file = UploadedFile(_file)
            _filename = wrapped_file.name
            file_size = wrapped_file.file.size
            Log.debug('Got file: "%s"' % str(_filename))
            Log.debug('Content type: "$s" % file.content_type')

            _file_url = DataManagerUtil.create_file(_file, _filename)
            Log.debug("Created file " + _filename)
            Log.debug('Uploaded file saving done')
            #settings imports

            _file_delete_url = ""  # settings.MULTI_FILE_DELETE_URL+'/'
            #getting thumbnail url using sorl-thumbnail
            _thumbnail = DataManagerUtil.create_photo_thumbnail(settings.SAVE_PREFIX + _filename, _filename+'_thumb.jpg')

            result.append({"name": _filename,
                           "size": file_size,
                           "url": _file_url,
                           "thumbnail_url": _thumbnail,
                           "delete_url": _file_delete_url,
                           "delete_type": "POST"})

        total_result = {
            'files': result
        }

        #checking for json data type
        #big thanks to Guy Shapiro
        _response_data = simplejson.dumps(total_result)
        if "application/json" in request.META['HTTP_ACCEPT_ENCODING']:
            mimetype = 'application/json'
        else:
            mimetype = 'text/plain'
        return HttpResponse(_response_data, mimetype=mimetype)


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


def _log_critical_error(message, send_mail, parameters=None, request_user=None, stack_trace=None):
    Log.fatal(message+':'+str(parameters))
    if send_mail:
        subject = 'Error on momends!'

        mail_message = 'An error occurred:\n'
        if request_user:
            mail_message += 'While processing the request for '+request_user.username+'\n'
        mail_message += message + '\n'
        if parameters:
            mail_message += 'Request parameters were:' + str(parameters)+'\n'
        if stack_trace:
            mail_message += str(stack_trace)

        msg = EmailMultiAlternatives(subject, mail_message, settings.DEFAULT_FROM_EMAIL, settings.ERROR_EMAIL_RECEIVERS)
        Log.debug('Sending mail with this body: '+mail_message)
        try:
            msg.send()
        except Exception as e:
            Log.error('Could not send error mail :) ->' + str(e))
