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
from DataManager.models import RawData
from Outputs.AnimationManager.models import UserInteraction
from Outputs.AnimationManager.models import OutData
from Outputs.AnimationManager.models import AnimationPlayStat
from Outputs.AnimationManager.models import Theme
from DataManager.DataEnrich.EnrichDataWorker import EnrichDataWorker
from social_auth.db.django_models import UserSocialAuth
from random import randint
from django.core.exceptions import ObjectDoesNotExist

class HomePageLoggedFormView(FormView):
    form_class = CreateMomendForm
    template_name = 'HomePageTemplate.html'
    def get_context_data(self, **kwargs):
        context =  super(HomePageLoggedFormView,self).get_context_data(**kwargs)
        context['user_top_momends'] = EnrichDataWorker.get_top_user_momends(user=self.request.user, max_count=10)
        context['public_top_momends'] = EnrichDataWorker.get_top_public_momends(max_count=20)
        return context

    def form_valid(self, form):
        momend_name = form.cleaned_data['momend_name']
        start_date = form.cleaned_data['start_date']
        finish_date = form.cleaned_data['finish_date']
        privacy = form.cleaned_data['privacy_type']
        _user = User.objects.get(username=self.request.user)
        dm = DataManager(_user)
        momend_id = dm.create_momend(name=momend_name, since=start_date,
            until=finish_date, duration=30, privacy=privacy, theme=Theme.objects.get(pk=form.cleaned_data['momend_theme']))
        status = dm.get_last_status()
        #TODO get status back to view
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

class ShowMomendView(TemplateView):
    template_name = 'ShowMomendTemplate.html'

    def dispatch(self, request, *args, **kwargs):
        play_stat = AnimationPlayStat()
        play_stat.momend_id = kwargs['id']
        if 'HTTP_REFERER' in request.META:
            play_stat.redirect_url = request.META['HTTP_REFERER']
        else:
            play_stat.redirect_url = 'Direct'
        if request.user:
            play_stat.user = User.objects.get(pk=request.user.id)
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
        _out_data_data = []
        _out_data_thumb = []
        for _out_data in _all_dis:
            if _out_data['raw']:
                _obj = RawData.objects.get(pk=_out_data['raw'])
                _out_data_data.append(_obj.data)
                _out_data_thumb.append(_obj.thumbnail)
        context['out_data_data'] = _out_data_data
        context['out_data_thumb'] = _out_data_thumb
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
    def post(self, request, *args, **kwargs): #TODO user check may be?
        queue = request.POST['queue']
        momend_id = request.POST['id']
        interaction = UserInteraction()
        interaction.momend_id = momend_id
        interaction.interaction = queue
        interaction.save()
        return HttpResponse('true',status=200)

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
        def get_redirect_url(self, pk):
            if self.request.user.is_authenticated():
                url = reverse('momends:home-screen',args=(pk))
            else:
                url = reverse('momends:main-screen',args=(pk))
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




