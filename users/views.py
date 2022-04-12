
from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.urls import reverse

from users.models import RequestPasswordUUID
from .forms import UserRegisterForm, UserLoginForm
from django.contrib.auth import authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import UserUpdateForm, UpdateProfileForm, ForgetPasswordForm, ResetPasswordForm, ChangePasswordForm

from django.contrib.auth import login as django_login
from django.urls import reverse
from django.utils import timezone
from .models import Profile, VerificationToken
from .utils import token_generator, send_email_link

from django.http import FileResponse
from .utils import token_generator
import uuid
from django.core.cache import cache


CACHE_LENGTH = 100


# Create your views here.
def register(request):
    is_resend = False

    if request.user.is_authenticated:
        return redirect("blog-home")

    if request.method == "POST":
        form  = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            # email = form.cleaned_data.get("email")
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password1")

            user = authenticate(username=username, password=password)
            if not user:
                return HttpResponse("FAIL CREATED USER")

                                    # profile is automatically created in signals module 
            profile = user.profile;
            
            cache_key = token_generator(CACHE_LENGTH)
            profile_reg_id = uuid.uuid4().hex 
            
            cache.set_many({cache_key: {profile_reg_id:profile.id}}, 240)
            
            messages.info(request, f"Your account has been created! check your verification link in your inbox")
            # user = authenticate(username = username, password=password)
            # vt = user.profile.verificationtoken
    
    else: # user ask resend verification link via GET request with query reg_key and profile_reg_id query params
        
        reg_key = request.GET.get("reg_key", "")
        profile_reg_id  = request.GET.get("profile_reg_id","")

        profile_id =  cache.get(reg_key,{}).get(profile_reg_id)

        if not profile_id:
            form = UserRegisterForm()
            return render(request, "users/register.html", {"form": form})
        
        else:
            is_resend = True

            # update reg_key in cache db
            cache.delete(reg_key)
            cache_key = token_generator(CACHE_LENGTH)
            cache.set_many({cache_key: {profile_reg_id:profile_id}}, 240)
        
        # try:
        #     vt = get_object_or_404(VerificationToken, token_uuid=token_uuid)
        #     vt.value = token_generator(54)
        #     vt.save()
        #     is_resend = True
        # except Http404:
        #     form =UserRegisterForm()
        #     return render(request, "users/register.html", {"form": form})
            

    ver_link = reverse("register") + "verify/" + cache_key + "?profile_reg_id=" + profile_reg_id
    ver_link = request.build_absolute_uri(ver_link)
    username = profile.user.username
    email = profile.user.email
    
    
    send_email_link("Email Verification",username, email, "Please verify your account", ver_link, "VERIFY MY ACCOUNT")
    
    # user click resend link
    if is_resend: messages.info(request, f"Resend email sucessfully")

    context = {
            "message": f"We have sent an email to <strong>{email}</strong> for verify your account in order to get access of our blog"
            " Please check your inbox, and follow the instruction we provide on the email."
            f" If you dont recieve the email, please resend the request, by clicking this link <a href=\"?reg_key={cache_key}&profile_reg_id={profile_reg_id}\">resend email</a>"
    }
            
    return render(request, "users/email_confirmation.html", context)

   


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

    profile_reg_id = request.GET.get("profile_reg_id")
    profile_id = cache.get(slug,{}).get(profile_reg_id)

    if not profile_id:
        return HttpResponse("invalid url")

    profile = get_object_or_404(Profile, id=profile_id)
    
    profile.is_email_verified = True
    profile.save()

    cache.delete(slug)

    django_login(request, profile.user)
    messages.success(request, f"Hello {profile.user.username} Welcome to our web")
    return redirect("blog-home")


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
            f_form.save()

            user, reset_key, reset_id = f_form.get_user(), f_form.get_reset_key(), f_form.get_reset_id()


            reset_link = reverse("reset-password") + "?reset_key=" +  reset_key +"&reset_id=" + reset_id
            reset_link = request.build_absolute_uri(reset_link)

            send_email_link("Reset Password Request",user.username, user.email, "Click link bellow to reset your password", reset_link, "RESET PASSWORD")

         
            context = {
            "message": f"We have sent an email to <strong>{user.email}</strong> for verify your account in order to get access for changing your password"
            " Please check your inbox, and follow the instruction we provide on the email."
            }
            
            return render(request, "users/email_confirmation.html", context)
            
        else:
            for err in f_form.errors.values():
                messages.error(request, err)
    
    instance=None
    if request.user.is_authenticated:
        instance = request.user
    f_form  = ForgetPasswordForm(instance=instance)

    return render(request, "users/forget_password.html", {"form": f_form, "form_name": "Request Reset Password", "button_name": "Send Link"})

# def request_reset_password(request, uuid):
 
#     reset_items = cache.get(uuid)

#     if not reset_items:
#         return HttpResponse("invalid request key")

    

#     request_id = get_object_or_404(RequestPasswordUUID, value=uuid)

#     diff = timezone.now() - request_id.created_at
#     if diff.seconds > 240: #4 minutes
#         # remove token row to save space
#         request_id.delete()
#         return HttpResponse("Your token was expired")
#     return redirect(reverse("reset-password") + "?password_id="+request_id.value)

def reset_password(request):
    # if request.user.is_authenticated:
    #     return redirect("change-password")
    
    if not cache.get(request.GET.get("reset_key",""),{}).get(request.GET.get("reset_id")):
        return redirect("login")

    isError = False
    if request.method == "POST":
        r_form  = ResetPasswordForm(request.POST, request=request)
        if r_form.is_valid():
            r_form.save();
            messages.success(request,"Your password has been reset")
            return redirect("blog-home")
        else:
            for err in r_form.errors.values():
                messages.error(request, err)
            isError = True
    r_form = ResetPasswordForm(request=request)
    return render(request, "users/forget_password.html", {"form": r_form, "form_name": "Reset Password", "button_name": "Reset Password", "isError": isError})

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


# protect media access, authenticated user is allowed, cons: media file is not static
@user_passes_test(lambda u: u.is_authenticated or u.is_staff, login_url="index-home")
def secure_profile_media(request, path):
    p_image = None
    profile_object = Profile.objects.filter(image="profile_pics/" + path)
    if profile_object.exists():
        p_image = profile_object[0].image
    response = FileResponse(p_image)
    return response


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