from django import forms
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm
from django_recaptcha.fields import ReCaptchaField
from django import forms
from .models import StateMusic, StateFestival



class CustomUserCreationForm(UserCreationForm):
    captcha = ReCaptchaField()

    class Meta:
        model = CustomUser
        fields = ('email', 'name', 'password1', 'password2', 'captcha')


class StateMusicForm(forms.ModelForm):
    class Meta:
        model = StateMusic
        fields = ['state', 'title', 'music_file', 'description']

class StateFestivalForm(forms.ModelForm):
    class Meta:
        model = StateFestival
        fields = ['state', 'title', 'image', 'description']
