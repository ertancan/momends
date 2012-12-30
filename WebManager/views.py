__author__ = 'goktan'

from django.views.generic.edit import FormView
from WebManager.forms import CreateMomendForm
from DataManager.DataManager import DataManager
from django.contrib.auth.models import User

class HomePageFormView(FormView):
    form_class = CreateMomendForm
    template_name = 'HomePageTemplate.html'
    success_url = ""
    def form_valid(self, form):
        momend_name = form.cleaned_data['momend_name']
        start_date = form.cleaned_data['start_date']
        finish_date = form.cleaned_data['finish_date']
        privacy = form.cleaned_data['privacy_type']
        ert = User.objects.get(username='ertan')
        dm = DataManager(ert)
        dm.create_momend(name=momend_name, since=start_date,
            until=finish_date, duration=30, privacy=privacy)


