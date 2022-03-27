from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django.utils import timezone


# upload_to function
# def upload_image(instance, filename):
#         print(dir(instance.user))
#         print("xxxxx",Profile.objects.get(id=instance.pk).user.get_username())
#         return f"profile_pics/{instance.user.username + filename}"

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default="default.png", upload_to="profile_pics")
    # image = models.ImageField(default="default.png", upload_to=upload_image)
    is_email_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"<{self.user.username} profile>"
    
    # get execute when profile is save
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        print(self.image.path)
        img = Image.open(self.image.path)
        if img.height > 300 or img.width > 300:
            output_size = (300,300)
            img.thumbnail(output_size)
            img.save(self.image.path)

class VerificationToken(models.Model):
    profile = models.OneToOneField(Profile, default=None, on_delete=models.CASCADE)
    value = models.CharField(max_length = 64)
    created_at = models.DateTimeField(default = timezone.now)
    token_uuid = models.CharField(max_length=32)
    def __str__(self):
        return f"<{self.value}>"

    
