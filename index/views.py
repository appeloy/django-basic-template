from django.shortcuts import render, redirect

def index(request):
    if request.user.is_authenticated:
        return redirect("blog-home")
    return render(request, "index/index.html")

def about(request):
    return render(request, 'index/about.html')
