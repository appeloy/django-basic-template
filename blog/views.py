from django.http import request
from django.shortcuts import render
from .models import Post
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


# Create your views here.
def home(request):
    context = {
        "posts": Post.objects.all()
    }
    return render(request, 'blog/home.html', context)
      
class PostListView(ListView):
    model = Post
    template_name = "blog/home.html"
    context_object_name = "posts"
    ordering = ["-date_posted"]
    paginate_by = 2

class PostDetailView(DetailView):
    model = Post
    template_name = "blog/post_detail.html"

class PostCreateView(LoginRequiredMixin,CreateView):
    model  =Post
    # template_name = post_form.html (default)
    fields = ["title", "content"] 

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request,f"New blog has been posted")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super(PostCreateView, self).get_context_data(**kwargs)
        context["form_name"] = "Create Post"
        context["form_button"] = "Post"
        return context

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    # template_name same as CreateView
    fields = ["title", "content"]

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request,f"blog has been updated")
        return super().form_valid(form)
    
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author
    
    def get_context_data(self, **kwargs):
        context = super(PostUpdateView, self).get_context_data(**kwargs)
        context["form_name"] = "Update Post"
        context["form_button"] = "Update"
        return context

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

def about(request):
    return render(request, 'blog/about.html', {"title": "About"})
