from django.shortcuts import render, redirect, HttpResponseRedirect, HttpResponse
from .forms import UserRegisterForm, UserLoginForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm, UpdateProfileForm

from django.contrib.auth import views as auth_views, login
from django.urls import reverse
from .models import Profile


# Create your views here.
def register(request):
    if request.method == "POST":
        form  = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get("email")
            messages.info(request, f"Your account has been created! check your verification link at {email}")
            return redirect("login")
    else:
        form  = UserRegisterForm()

    from django.core.mail import send_mail
    send_mail("head mail", "this is body", "business.nubcake@gmail.com", ["anggikharismaputra@gmail.com"], fail_silently=False)
    
    return render(request, "users/register.html", {"form": form})



class CustomLoginView(auth_views.LoginView):
    template_name = "login.html"
    authentication_form = UserLoginForm

    # get execute when form is submited, after UserLoginForm.clean() executed (check django documentation)
    def form_valid(self, form):
        user = form.get_user()
        # check account email verified status
        if not user.profile.is_email_verified:
            messages.warning(self.request, f"Can't login yet, your account is unverified, check inbox email of {user.email}")
            return HttpResponseRedirect("")
        login(self.request, form.get_user())
        return HttpResponseRedirect(reverse('profile'))


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

