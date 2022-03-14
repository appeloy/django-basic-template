from django.db import models
from django.contrib.auth.models import User, AbstractUser
from PIL import Image
from django.utils import timezone




# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default="default.png", upload_to="profile_pics")
    is_email_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} profile"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.image.path)
        if img.height > 300 or img.width > 300:
            output_size = (300,300)
            img.thumbnail(output_size)
            img.save(self.image.path)

class VerificationToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    value = models.CharField(max_length = 100)
    created_at = models.DateTimeField(default = timezone.now)

    
