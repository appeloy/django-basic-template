"""django_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from users import views as user_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # path("login/", auth_views.LoginView.as_view(template_name="users/login.html"), name="login"),
    path("login/", user_views.login, name="login"),
    path("logout/", auth_views.LogoutView.as_view(template_name="users/logout.html"), name="logout"),
    path("profile/", user_views.profile, name="profile"),
    path("register/", user_views.register, name="register"),
    path("forget-password/", user_views.forget_password, name="forget-password"),
    path("change-password/", user_views.change_password,name="change-password"),
    path("request-reset-password/<slug:uuid>/", user_views.request_reset_password, name="request-reset-password"),
    path("reset-password/", user_views.reset_password, name="reset-password"),
    path("verify/<slug:token_uuid>/<slug:slug>/", user_views.email_verification, name="email-verification"),
    path("", include("blog.urls")),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)