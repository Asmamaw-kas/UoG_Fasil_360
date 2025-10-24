from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .models import Photo, FeaturedPhoto

@receiver(m2m_changed, sender=Photo.likes.through)
def update_featured_status(sender, instance, action, **kwargs):
    """
    Automatically feature photos that reach a certain like threshold
    """
    if action == 'post_add':
        like_threshold = 10  # Adjust this threshold as needed
        
        if instance.total_likes() >= like_threshold and not instance.is_featured:
            instance.is_featured = True
            instance.save()
            
            # Create featured photo entry if it doesn't exist
            FeaturedPhoto.objects.get_or_create(
                photo=instance,
                defaults={'is_active': True}
            )

@receiver(post_save, sender=Photo)
def handle_featured_photo(sender, instance, created, **kwargs):
    """
    Manage FeaturedPhoto entries when photo is saved
    """
    if instance.is_featured:
        FeaturedPhoto.objects.get_or_create(
            photo=instance,
            defaults={'is_active': True}
        )
    else:
        # Remove from featured photos if unfeatured
        FeaturedPhoto.objects.filter(photo=instance).update(is_active=False)