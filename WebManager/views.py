__author__ = 'goktan'

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.views.generic.edit import FormView
from django.views.generic.detail import DetailView
from django.views.generic.base import TemplateView

from WebManager.forms import CreateMomendForm
from DataManager.DataManager import DataManager
from DataManager.models import Momend



class HomePageFormView(FormView):
    form_class = CreateMomendForm
    template_name = 'HomePageTemplate.html'
    def form_valid(self, form):
        momend_name = form.cleaned_data['momend_name']
        start_date = form.cleaned_data['start_date']
        finish_date = form.cleaned_data['finish_date']
        privacy = form.cleaned_data['privacy_type']
        ert = User.objects.get(username='goktan')
        dm = DataManager(ert)
        momend_id = dm.create_momend(name=momend_name, since=start_date,
            until=finish_date, duration=30, privacy=privacy)
        self.success_url = reverse('momends:show-momend', args=(momend_id,))
        return super(HomePageFormView,self).form_valid(form)


class ShowMomendView(TemplateView):
    context_object_name = 'momend'
    template_name = 'ShowMomendTemplate.html'

class GetMomendView(DetailView):
    model = Momend
    context_object_name = 'momend'
    template_name = 'GetMomendTemplate.html'

