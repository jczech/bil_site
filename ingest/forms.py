from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import MinimalImgMetadata


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Required')
    last_name = forms.CharField(max_length=30, required=False, help_text='Required')
    email = forms.EmailField(max_length=254, help_text='Required. A valid email address.')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )

class MIMForm(forms.ModelForm):

    class Meta:
        model = MinimalImgMetadata
        fields = (
            'project_name',
            'organization_name',
            'project_description',
            'submitter_email')