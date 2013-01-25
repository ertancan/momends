__author__ = 'goktan'
from django import forms
from datetime import date
from dateutil.relativedelta import relativedelta
from django.forms import widgets
from DataManager.models import Momend
from Outputs.AnimationManager.models import Theme


class CreateMomendForm(forms.Form):
    momend_name = forms.CharField(max_length=255, min_length=4, required=True, label='Name', widget=forms.TextInput(attrs={'class':'modal-form-input'}))
    start_date = forms.DateTimeField(widget=widgets.DateInput(format='%d %b, %Y', attrs={'class':'modal-form-input'}), required=True,
        input_formats=['%d %b, %Y'], initial=(date.today()-relativedelta(months = +1)))
    finish_date = forms.DateTimeField(widget=widgets.DateInput(format='%d %b, %Y', attrs={'class':'modal-form-input'}), required=True,
        input_formats=['%d %b, %Y'], initial=date.today())
    privacy_type = forms.ChoiceField(choices=[[Momend.PRIVACY_CHOICES[key],key]
                                              for key in Momend.PRIVACY_CHOICES.keys()], widget=forms.Select(attrs={'class':'modal-form-input'}))

    THEME_CHOICES = dict()
    for theme in Theme.objects.all():
        THEME_CHOICES[theme.name] = theme.pk
    momend_theme = forms.ChoiceField(choices=[[THEME_CHOICES[key],key] for key in THEME_CHOICES.keys()], widget=forms.Select(attrs={'class':'modal-form-input'}) )

class SettingsForm(forms.Form):
    """for further usage"""
    pass
