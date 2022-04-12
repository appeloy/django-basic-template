from blog.models import Post
from django.core.paginator import Paginator, EmptyPage
from django.http import JsonResponse
from .serializer import PostSerializer
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

import time

# Create your views here.

@require_http_methods(["GET"])
@login_required
def posts(request):
    p = Paginator(Post.objects.all().order_by("-date_posted"), 3)
    r_page = request.GET.get("page", 1)
    time.sleep(3)
    try:
        return JsonResponse(
            {"data": [PostSerializer(o).as_dict() for o in p.page(int(r_page)).object_list]
        },status=200)

    except EmptyPage:
        return JsonResponse({
             "data": []
        }, status=404)

        