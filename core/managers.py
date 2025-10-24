from django.db import models
from django.utils import timezone

class PhotoManager(models.Manager):
    def featured(self):
        return self.get_queryset().filter(is_featured=True, is_approved=True)
    
    def by_batch(self, batch):
        return self.get_queryset().filter(category__batch=batch, is_approved=True)
    
    def recent(self, days=30):
        return self.get_queryset().filter(
            created_at__gte=timezone.now() - timezone.timedelta(days=days),
            is_approved=True
        )

class DocumentManager(models.Manager):
    def by_type(self, doc_type):
        return self.get_queryset().filter(document_type=doc_type, is_approved=True)
    
    def recent(self, days=30):
        return self.get_queryset().filter(
            created_at__gte=timezone.now() - timezone.timedelta(days=days),
            is_approved=True
        )