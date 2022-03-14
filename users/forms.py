from ast import Pass
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
# from django.forms import fields
from .models import Profile

from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate

class UserRegisterForm(UserCreationForm):
    email  = forms.EmailField()

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    # Validate form input
    def clean(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get("username")
        
        if User.objects.filter(email=email).exists():
            raise ValidationError("email already exists")  #apparently this Validation Error pipe in into django.congtrib.message
        
        if User.objects.filter(username=username):
            raise ValidationError("username already exists")
        
        return self.cleaned_data

class UserLoginForm(AuthenticationForm):
    pass


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["username", "email"]

class UpdateProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields  = ["image"]