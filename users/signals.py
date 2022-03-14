from multiprocessing.sharedctypes import Value
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile, VerificationToken
from .utils import token_generator, send_email_verification_link

import hashlib


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance)
        token = token_generator(25)
        VerificationToken.objects.create(profile=profile, value=token)
        send_email_verification_link(instance.username, instance.email, f"http://localhost:8000/verify/{instance.username}/{token}")

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()
    # instance.(maybe follow the reciever object?).save()