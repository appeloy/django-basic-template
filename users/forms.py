from ast import Pass
from dataclasses import Field
import email
from pyexpat import model
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
# from django.forms import fields
from .models import Profile

from django.core.exceptions import ValidationError
from .utils import send_email_verification_link
import uuid
from .models import RequestPasswordUUID

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
        
        if User.objects.filter(username=username).exist():
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

class ForgetPasswordForm(forms.Form):
    email = forms.EmailField(label="Enter your email", required=True)

    def clean(self):
        super().clean()
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            print("xx",email)
            raise ValidationError(f"email {email} is not exist")
        return self.cleaned_data

    def is_valid(self):
        return self.is_bound and not self.errors

    def save(self):
        user = User.objects.get(email=self.cleaned_data.get("email"))
        o = RequestPasswordUUID.objects.create(owner=user, value=uuid.uuid4().hex)
        o.save()
        send_email_verification_link("Click link bellow to reset your password", o.owner.email, f"http://localhost:8000/request-reset-password/{o.value}/")

