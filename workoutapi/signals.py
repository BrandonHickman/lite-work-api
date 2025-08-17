from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.conf import settings
from .models.profile import Profile

# This function runs after a User is saved
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:  # only run when the user is first created
        Profile.objects.get_or_create(user=instance)


# What’s happening here:

# @receiver(post_save, sender=User) → Listens for the post_save event on the User model.

# created → Boolean that’s True if the object was just created (not updated).

# Profile.objects.create(user=instance) → Creates a matching profile.

# This is automatic, so keep this in mind when debugging.