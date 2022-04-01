from django.contrib import admin
from .models import Profile, VerificationToken, RequestPasswordUUID

# Register your models here.
admin.site.register([Profile, VerificationToken, RequestPasswordUUID])