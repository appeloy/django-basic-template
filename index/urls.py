from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="index-home"),
    path("about/", views.about, name="index-about")
]