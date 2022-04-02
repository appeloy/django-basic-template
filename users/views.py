from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.urls import reverse

from users.models import RequestPasswordUUID
from .forms import UserRegisterForm, UserLoginForm
from django.contrib.auth import authenticate
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm, UpdateProfileForm, ForgetPasswordForm, ResetPasswordForm, ChangePasswordForm

from django.contrib.auth import login as django_login
from django.urls import reverse
from django.utils import timezone
from .models import Profile, VerificationToken

from .utils import token_generator, send_email_verification_link
from django.http.response import Http404


# Create your views here.
def register(request):

    if request.user.is_authenticated:
        return redirect("blog-home")

    if request.method == "POST":
        form  = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            # email = form.cleaned_data.get("email")
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password1")

            messages.info(request, f"Your account has been created! check your verification link in your inbox")
            user = authenticate(username = username, password=password)
            vt = user.profile.verificationtoken
    
    else:
        token_uuid  = request.GET.get("token_uuid")
        try:
            vt = get_object_or_404(VerificationToken, token_uuid=token_uuid)
            vt.value = token_generator(54)
            vt.save()
        except Http404:
            form =UserRegisterForm()
            return render(request, "users/register.html", {"form": form})
            

    ver_link = reverse("register") + "verify/" + vt.value
    ver_link = request.build_absolute_uri(ver_link)
    resend_link = vt.token_uuid
    username = vt.profile.user.username
    email = vt.profile.user.email
    
    
    send_email_verification_link("Email Verification",username, email, "Please verify your account", ver_link, "VERIFY MY ACCOUNT")
    messages.info(request, f"Resend email sucessfully")

    context = {
            "message": f"We have sent an email to <strong>{email}</strong>."
            " Please check your inbox, and follow the instruction we provide on the email."
            f" If you dont recieve the email, please resend the request, by clicking this link <a href=\"?token_uuid={resend_link}\">resend email</a>"
    }
            
    return render(request, "users/email_confirmation.html", context)

   


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
        form = UserLoginForm(request,data=request.POST)
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

    form = UserLoginForm(request)
    return render(request, "users/login.html", {"form": form})


def email_verification(request,slug):
    
    token_object = get_object_or_404(VerificationToken, value=slug)
    
    # check if token is already expired
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
    return render(request, "users/forget_password.html", {"form": f_form, "form_name": "Request Reset Password", "button_name": "Send Link"})

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
    return render(request, "users/forget_password.html", {"form": r_form, "form_name": "Reset Password", "button_name": "Reset Password"})

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
    return render(request, "users/forget_password.html", {"form": form, "form_name": "Change Password", "button_name": "Change Password"})
    