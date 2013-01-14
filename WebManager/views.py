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
from Outputs.AnimationManager.models import AnimationPlayStat,UserInteraction
from Outputs.AnimationManager.models import Theme
from DataManager.DataEnrich.EnrichDataWorker import EnrichDataWorker
from social_auth.db.django_models import UserSocialAuth
from random import randint

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
        self.success_url = reverse('momends:show-momend', args = (momend_id,) )
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

    def get_context_data(self, *args, **kwargs):
        context = super(ShowMomendView, self).get_context_data(**kwargs)

        play_stat = AnimationPlayStat()
        play_stat.momend_id = context['params']['id']
        if 'HTTP_REFERER' in self.request.META:
            play_stat.redirect_url = self.request.META['HTTP_REFERER']
        else:
            play_stat.redirect_url = 'Direct'
        if self.request.user:
            play_stat.user = User.objects.get(pk=self.request.user.id)
        play_stat.save()
        return context

class GetMomendView(TemplateView):
    template_name = 'GetMomendTemplate.html'
    def get_context_data(self, **kwargs):
        context = super(GetMomendView, self).get_context_data(**kwargs)
        obj = Momend.objects.get(pk = kwargs['id'])
        if obj.privacy == Momend.PRIVACY_CHOICES['Private']:
            if obj.owner != self.request.user:
                context['momend'] = '{"error":"not authorised"}'
                return context
        context['momend'] = obj.toJSON()
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




