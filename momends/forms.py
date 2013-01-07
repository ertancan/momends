__author__ = 'goktan'

from registration.forms import RegistrationFormUniqueEmail
from captcha.fields import ReCaptchaField

class RegistrationFormCaptcha(RegistrationFormUniqueEmail):
    captcha = ReCaptchaField(attrs={'theme': 'white'})


#class RegistrationFormUniqueEmailRecaptcha(RegistrationFormUniqueEmail, RegistrationFormCaptcha):
#    pass