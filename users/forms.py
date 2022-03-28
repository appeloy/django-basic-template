import email
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
# from django.forms import fields
from .models import Profile

from django.core.exceptions import ValidationError
from .utils import send_email_verification_link
from django.db.utils import IntegrityError
import uuid
from .models import RequestPasswordUUID, VerificationToken

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
        
        if User.objects.filter(username=username).exists():
            raise ValidationError("username already exists")
        
        return self.cleaned_data

class UserLoginForm(AuthenticationForm):
    pass
    
        


class UserUpdateForm(forms.ModelForm):
    # email = forms.EmailField()

    class Meta:
        model = User
        # fields = ["username", "email"]
        fields = ["username"]

class UpdateProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields  = ["image"]

class ForgetPasswordForm(forms.Form):
    email = forms.EmailField(label="Enter your email", required=True)

    def clean(self):
        super().clean()
        email = self.cleaned_data.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValidationError(f"user with email {email} is not exist")
        try:
            self.__request_p = RequestPasswordUUID.objects.create(owner=user,value=uuid.uuid4().hex)
        except IntegrityError:
            raise ValidationError(f"You have request reset password")
        return self.cleaned_data

    def is_valid(self):
        return self.is_bound and not self.errors

    def save(self):
        self.__request_p.save()
        send_email_verification_link("Click link bellow to reset your password", self.__request_p.owner.email, f"http://localhost:8000/request-reset-password/{self.__request_p.value}/")


class ResetPasswordForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(ResetPasswordForm, self).__init__(*args, **kwargs)

    def clean(self):
        super().clean()
        password1 = self.cleaned_data.get("new_password")
        password2 = self.cleaned_data.get("confirm_password")
        if password1 != password2:
            raise ValidationError("Password isn't match")
        if self.request.user.check_password(password1):
            raise ValidationError("New password cannot same as old password")
        return self.cleaned_data
    
    def save(self):
        user = self.request.user
        if user:
            user.set_password(self.cleaned_data.get("new_password"))
            user.save();



    
     