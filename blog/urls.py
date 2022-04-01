from blog.models import Post
from django.urls import path
from . import views


# using django view
# from .views import PostListView, PostDetailView, PostCreateView, PostUpdateView, PostDeleteView, post
# urlpatterns = [
#     path("", PostListView.as_view(), name="blog-home"),
#     path("post/<int:pk>", PostDetailView.as_view(), name="post-detail"),
#     path("post/new", PostCreateView.as_view(), name="post-create"),
#     path("post/<int:pk>/update", PostUpdateView.as_view(), name="post-update"),
#     path("post/<int:pk>/delete", PostDeleteView.as_view(), name="post-delete"),
#     path("about/", views.about, name="blog-about")
# ]

#using view function
urlpatterns = [
    path("", views.home, name="blog-home"),
    path("<int:post_id>/", views.post, name="post-detail"),
    path("new/", views.post_create, name="post-create"),
    path("<int:post_id>/update/", views.post_update, name="post-update"),
    path("<int:post_id>/delete/", views.post_delete, name="post-delete")
]

