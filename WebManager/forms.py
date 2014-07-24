__author__ = 'goktan'
from django import forms

class SettingsForm(forms.Form):
    """for further usage"""
    pass


# -*- coding: utf-8 -*-
from django import forms

class DocumentForm(forms.Form):
    files = forms.FileField(
        label='Select a file',
        help_text='max. 42 megabytes'
    )