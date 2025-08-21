from django.conf import settings
from django.db import models
from django.utils import timezone

class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    bio = models.TextField(blank=True, default="")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    challenge_goal = models.PositiveIntegerField(null=True, blank=True)
    challenge_window_days = models.PositiveIntegerField(null=True, blank=True)
    challenge_label = models.TextField(blank=True)
    challenge_started_at = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username