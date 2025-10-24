from django.db import models
from django.contrib.auth.models import AbstractUser

class UserProfile(models.Model):
    user = models.OneToOneField('core.User', on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True)
    social_links = models.JSONField(default=dict, blank=True)  # Store social media links
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}'s Profile"