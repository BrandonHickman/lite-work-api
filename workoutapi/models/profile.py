from django.contrib.auth.models import User
from django.conf import settings
from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, default="")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)  # or URLField if you prefer
    challenge_goal = models.PositiveIntegerField(null=True, blank=True)  # workouts per 30 days
    challenge_started_at = models.DateField(null=True, blank=True)  # optional (defaults can be “30 days rolling”)


    def __str__(self):
        return self.user.username