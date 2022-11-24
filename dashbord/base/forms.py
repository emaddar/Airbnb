# from django import forms
# from django.core import validators
from . import models

# class SignUp(forms.Form):
#     user = forms.CharField(label='User Name', max_length=100)
#     email = forms.EmailField(label='Email', max_length=100)
#     password = forms.CharField(widget=forms.PasswordInput, label='PassWord')
#     botcatcher = forms.CharField(required=False, widget=forms.HiddenInput, validators=[validators.MaxLengthValidator(0)])




# from django import forms
# from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class UserCreateForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = models.User
        fields = ('username', 'first_name','password1','password2','email',  'last_name')