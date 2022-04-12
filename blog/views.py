from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from .models import Post
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required


from . import forms


# Create your views here.
@login_required
def home(request):
    context = {
        # "posts": Post.objects.all().order_by("-date_posted")
    }
    return render(request, 'blog/home.html', context)

@login_required
def post(request, post_id):
    o = get_object_or_404(Post, pk=post_id)
    context = {
        "object": o
    }    
    return render(request, "blog/post_detail.html", context)

@login_required
def post_create(request):
    if request.method =="POST":
        form = forms.PostCreateForm(request.POST, request=request)
        if form.is_valid():
            form.save()
            messages.success(request,"New post created")
            return redirect("blog-home")
    
    else:
        form = forms.PostCreateForm(request=request)
    
    context = {
            "form": form,
            "form_name": "Create Post",
            "form_button": "Post",
    }
    return render(request, "blog/post_form.html", context)
    
    return HttpResponse("post create view")


@login_required
def post_delete(request, post_id):
    o = get_object_or_404(Post, id=post_id)
    # try:
    #     o = Post.objects.get(id=post_id, author=request.user)
    # except:
    #     return HttpResponse("Not authorized or id not found")

    form = forms.PostDeleteForm(instance=o)

    context = {
        "object": o,
    }

    if request.method == "POST":
        form = forms.PostDeleteForm(request.POST, instance=o)
        if form.is_valid():
            form.save()
            messages.success(request,"Post deleted")
            return redirect("blog-home")
   
    else:
        return render(request, "blog/post_confirm_delete.html", context)

    return HttpResponse("post delete view")


@login_required
def post_update(request, post_id):
    
    o = get_object_or_404(Post, id=post_id)
    
    # try:
    #     o = Post.objects.get(id=post_id, author=request.user)
    # except:
    #     return HttpResponse("Not authorized or id not found")

    if request.method =="POST":
        form = forms.PostUpdateForm(request.POST, instance=o)
        if form.is_valid():
            form.save()
            messages.success(request, "Post Updated")
            return redirect("blog-home")
    
    else:
        form = forms.PostUpdateForm(instance=o)
    
    context = {
            "form": form,
            "form_name": "Update Post",
            "form_button": "update",
    }
    return render(request, "blog/post_form.html", context)





# codes bellow uing dango view
# class PostListView(ListView):
#     model = Post
#     template_name = "blog/home.html"
#     context_object_name = "posts"
#     ordering = ["-date_posted"]
#     paginate_by = 5

# class PostDetailView(DetailView):
#     model = Post
#     template_name = "blog/post_detail.html"

# class PostCreateView(LoginRequiredMixin,CreateView):
#     model  =Post
#     # template_name = post_form.html (default)
#     fields = ["title", "content"] 

#     def form_valid(self, form):
#         form.instance.author = self.request.user
#         messages.success(self.request,f"New blog has been posted")
#         return super().form_valid(form)
    
#     def get_context_data(self, **kwargs):
#         context = super(PostCreateView, self).get_context_data(**kwargs)
#         context["form_name"] = "Create Post"
#         context["form_button"] = "Post"
#         return context

# class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
#     model = Post
#     # template_name same as CreateView
#     fields = ["title", "content"]

#     def form_valid(self, form):
#         form.instance.author = self.request.user
#         messages.success(self.request,f"blog has been updated")
#         return super().form_valid(form)
    
#     def test_func(self):
#         post = self.get_object()
#         return self.request.user == post.author
    
#     def get_context_data(self, **kwargs):
#         context = super(PostUpdateView, self).get_context_data(**kwargs)
#         context["form_name"] = "Update Post"
#         context["form_button"] = "Update"
#         return context

# class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
#     model = Post
#     success_url = '/'

#     def test_func(self):
#         post = self.get_object()
#         return self.request.user == post.author