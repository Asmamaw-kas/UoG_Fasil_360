from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Photo, FeaturedPhoto

class Command(BaseCommand):
    help = 'Update featured photos based on likes and time criteria'
    
    def handle(self, *args, **options):
        # Feature photos with high likes
        popular_photos = Photo.objects.filter(
            likes__gte=10,
            is_approved=True,
            is_featured=False
        )
        
        for photo in popular_photos:
            photo.is_featured = True
            photo.save()
            self.stdout.write(
                self.style.SUCCESS(f'Featured photo: {photo.title}')
            )
        
        # Unfeature old featured photos (older than 30 days)
        old_featured = FeaturedPhoto.objects.filter(
            featured_from__lt=timezone.now() - timezone.timedelta(days=30),
            is_active=True
        )
        
        for featured in old_featured:
            featured.is_active = False
            featured.save()
            featured.photo.is_featured = False
            featured.photo.save()
            self.stdout.write(
                self.style.WARNING(f'Unfeatured old photo: {featured.photo.title}')
            )