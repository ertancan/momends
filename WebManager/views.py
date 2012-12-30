__author__ = 'goktan'

from django.views.generic.edit import FormView
from WebManager.forms import CreateMomendForm

class HomePageFormView(FormView):
    form_class = CreateMomendForm
    template_name = 'HomePageTemplate.html'
    success_url = ""
