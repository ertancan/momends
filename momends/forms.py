__author__ = 'goktan'

from registration.forms import RegistrationFormUniqueEmail
from registration.forms import attrs_dict
from captcha.fields import ReCaptchaField
from django import forms
from django.utils.translation import ugettext_lazy as _

class RegistrationFormMomends(RegistrationFormUniqueEmail):
    #captcha = ReCaptchaField(attrs={'theme': 'white'})
    username = forms.RegexField(regex=r'^[a-z A-Z]+[\w.@+-]+$',
        max_length=30,
        widget=forms.TextInput(attrs=attrs_dict),
        label=_("Username"),
        error_messages={'invalid': _("This value may contain only letters, numbers and @/./+/-/_ characters and it should"
                                     "start with a character.")})


#class RegistrationFormUniqueEmailRecaptcha(RegistrationFormUniqueEmail, RegistrationFormCaptcha):
#    pass