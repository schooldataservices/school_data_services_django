from django.db.models.signals import post_save  #signal that gets fired after object is saved
from django.contrib.auth.models import User     #when user is created we want a post save
from django.dispatch import receiver
from .models import Profile

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        print(f"Creating profile for user: {instance.username}")  # Debugging information
        profile = Profile.objects.create(user=instance)

        # Explicitly save the default image if not set
        if not profile.image:  # This checks if the image field is empty
            profile.image = "profile_pics/default.jpg"
            profile.save()  # Save the change

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()

#Rather than going through admin page, once a user is created through initial Django form it will be passed 
#to the created User profiles.
