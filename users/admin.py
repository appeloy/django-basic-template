from django.contrib import admin
from .models import Profile, VerificationToken

# Register your models here.
admin.site.register([Profile, VerificationToken])