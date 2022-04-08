from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from pathlib import Path

urlpatterns = [
      # path("login/", auth_views.LoginView.as_view(template_name="users/login.html"), name="login"),
    path("login/", views.login, name="login"),
    path("logout/", auth_views.LogoutView.as_view(template_name="users/logout.html"), name="logout"),
    path("profile/", views.profile, name="profile"),
    path("register/", views.register, name="register"),
    path("forget-password/", views.forget_password, name="forget-password"),
    path("change-password/", views.change_password,name="change-password"),
    path("request-reset-password/<slug:uuid>/", views.request_reset_password, name="request-reset-password"),
    path("reset-password/", views.reset_password, name="reset-password"),
    path("register/verify/<slug:slug>/", views.email_verification, name="email-verification"),
]