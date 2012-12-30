__author__ = 'goktan'
from django import forms
from datetime import date
from dateutil.relativedelta import relativedelta
from django.forms import widgets
from DataManager.models import Momend


class CreateMomendForm(forms.Form):
    momend_name = forms.CharField(max_length=255, min_length=4, required=True, label='Name')
    start_date = forms.DateField(widget=widgets.DateInput(format='%d %b, %Y'), required=True,
        input_formats=['%d %b, %Y'], initial=(date.today()-relativedelta(months = +1)))
    finish_date = forms.DateField(widget=widgets.DateInput(format='%d %b, %Y'), required=True,
        input_formats=['%d %b, %Y'], initial=date.today())
    privacy_type = forms.ChoiceField(choices=Momend.PRIVACY_CHOICES)
