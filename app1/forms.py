from django import forms
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm
from django_recaptcha.fields import ReCaptchaField
from django import forms
from .models import StateMusic, StateFestival,CommunityData,State_details



class CustomUserCreationForm(UserCreationForm):
    captcha = ReCaptchaField()

    class Meta:
        model = CustomUser
        fields = ('email', 'name', 'password1', 'password2', 'captcha')


class StateMusicForm(forms.ModelForm):
    class Meta:
        model = StateMusic
        fields = ['state', 'title', 'music_file', 'description']
        widgets = {
            'state': forms.HiddenInput()
        }

class StateFestivalForm(forms.ModelForm):
    class Meta:
        model = StateFestival
        fields = ['state', 'title', 'image', 'description']
        widgets = {
            'state': forms.HiddenInput()
        }


class CommunityDataForm(forms.ModelForm):
    class Meta:
        model = CommunityData
        fields = ['title','state', 'category', 'image', 'description']
    
    def __init__(self, *args, **kwargs):
        # Optional: hide state for state-specific posts
        hide_state = kwargs.pop('hide_state', False)
        super().__init__(*args, **kwargs)
        if hide_state:
            self.fields['state'].widget = forms.HiddenInput()
        else:
            self.fields['state'].queryset = State_details.objects.all()
            self.fields['state'].required = True  # user must pick a state


from django import forms
from .models import CustomUser

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('name', 'avatar', 'bio')
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 4,
                'placeholder': 'Tell something about yourself...'
            }),
            'avatar': forms.ClearableFileInput(attrs={
                'class': 'block w-full text-sm text-gray-600 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 focus:outline-none'
            }),
        }



from django import forms

class ImageUploadForm(forms.Form):
    image = forms.ImageField()