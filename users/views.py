import email
from pydoc import plain
from django.shortcuts import render, redirect, HttpResponseRedirect, HttpResponse

from users.models import RequestPasswordUUID
from .forms import UserRegisterForm, UserLoginForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm, UpdateProfileForm, ForgetPasswordForm, ResetPasswordForm, ChangePasswordForm

from django.contrib.auth import views as auth_views, login as django_login
from django.urls import reverse
from django.utils import timezone
from .models import VerificationToken

from django.contrib.auth.forms import AuthenticationForm


# Create your views here.
def register(request):
    if request.user.is_authenticated:
        return redirect("blog-home")

    if request.method == "POST":
        form  = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get("email")
            messages.info(request, f"Your account has been created! check your verification link in your inbox")
            return redirect("login")
    else:
        form  = UserRegisterForm()

    return render(request, "users/register.html", {"form": form})



# class CustomLoginView(auth_views.LoginView):
#     template_name = "login.html"
#     authentication_form = UserLoginForm

#     # get execute when form is submited, after UserLoginForm.clean() executed (check django documentation)
#     def form_valid(self, form):
#         user = form.get_user()
#         # check account email verified status
#         if not user.profile.is_email_verified:
#             messages.warning(self.request, f"Can't login yet, your account is unverified, check inbox email of {user.email}")
#             return HttpResponseRedirect("")
#         login(self.request, form.get_user())
#         return redirect("blog-home")

def login(request):
    if request.user.is_authenticated:
        return redirect("profile")

    if request.method == "POST":
        form = AuthenticationForm(request,data=request.POST)
        if form.is_valid():
            user = form.get_user();
            if not user.is_staff and not user.profile.is_email_verified:
                messages.warning(request, f"Can't login yet, your account is unverified, check inbox email of {user.email}")
                return redirect("login")
            django_login(request, form.get_user())
            return redirect("blog-home")
        else:
            for err in form.errors.values():
                messages.error(request, err)
    form = AuthenticationForm()
    return render(request, "users/login.html", {"form": form})


def email_verification(request, token_uuid, slug):
    if not VerificationToken.objects.filter(token_uuid=token_uuid).exists():
        return HttpResponse("invalid url")
    try:
        token_object =  VerificationToken.objects.get(value=slug)
    except VerificationToken.DoesNotExist:
        return HttpResponse("404 (token doesnt exist)")

    # check if token is not expired
    diff = timezone.now() - token_object.created_at
    if diff.seconds > 240: #4 minutes
        # remove token row to save space
        token_object.delete()
        return HttpResponse("Your token was expired")

    profile = token_object.profile
    profile.is_email_verified = True
    profile.save()

    django_login(request, profile.user)
    messages.success(request, f"Hello {profile.user.username} Welcome to our web")
    # remove token row to save space
    token_object.delete()

    return redirect("blog-home")


@login_required
def profile(request):
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Your account has been updated!")
            return redirect("profile")
    
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = UpdateProfileForm(instance=request.user.profile)


    context = {
        "u_form":u_form,
        "p_form": p_form
    }
    return render(request, "users/profile.html", context)


def forget_password(request):
    if request.method == "POST":
        f_form = ForgetPasswordForm(request.POST)
        if f_form.is_valid():
            # send uuid link /request-reset-password
            print("form is valid!")
            f_form.save()
            return HttpResponse("send email to " + f_form.cleaned_data.get("email"))
        else:
            for err in f_form.errors.values():
                messages.error(request, err)
    
    instance = None
    if request.user.is_authenticated:
        instance = request.user
    f_form  = ForgetPasswordForm(instance=instance)
    return render(request, "users/forget_password.html", {"form": f_form})

def request_reset_password(request, uuid):
    try:
        request_id = RequestPasswordUUID.objects.get(value=uuid)
    except:
        return HttpResponse("invalid url")

    diff = timezone.now() - request_id.created_at
    if diff.seconds > 240: #4 minutes
        # remove token row to save space
        request_id.delete()
        return HttpResponse("Your token was expired")
    return redirect(reverse("reset-password") + "?password_id="+request_id.value)


def reset_password(request):
    # if request.user.is_authenticated:
    #     return redirect("change-password")
    if request.method == "POST":
        r_form  = ResetPasswordForm(request.POST, request=request)
        if r_form.is_valid():
            r_form.save();
            messages.success(request,"Your password has been reset")
            return redirect("blog-home")
        else:
            for err in r_form.errors.values():
                messages.error(request, err)
    r_form = ResetPasswordForm(request=request)
    return render(request, "users/forget_password.html", {"form": r_form})

@login_required
def change_password(request):
    if request.method == "POST":
        form  = ChangePasswordForm(request.POST, request=request)
        if form.is_valid():
            form.save();
            return redirect("blog-home")
        else:
            for err in form.errors.values():
                messages.error(request, err)
    form = ChangePasswordForm(request=request)
    return render(request, "users/forget_password.html", {"form": form})
    