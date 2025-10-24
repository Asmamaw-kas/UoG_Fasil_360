from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from .managers import PhotoManager, DocumentManager
from django.contrib.contenttypes.fields import GenericRelation

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('representative', 'Representative'),
        ('admin', 'Admin'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='student')
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=100)
    campus = models.CharField(max_length=100)
    batch = models.CharField(max_length=10)  # GC 2026, GC 2027, etc.
    is_verified = models.BooleanField(default=False)
    is_representative = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(null=True, blank=True)
    profile_views = models.PositiveIntegerField(default=0)
    
    # Override username field to use email
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.batch})"

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    batch_specific = models.BooleanField(default=False)
    batch = models.CharField(max_length=10, blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name

class Photo(models.Model):
    PHOTO_TYPE_CHOICES = (
        ('celebration', 'Celebration'),
        ('general', 'General'),
        ('reward', 'Reward'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='photos/')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    photo_type = models.CharField(max_length=20, choices=PHOTO_TYPE_CHOICES, default='general')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, related_name='photo_likes', blank=True)
    is_featured = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
   
    
    objects = PhotoManager()
    
    def total_likes(self):
        return self.likes.count()
    
    
    def __str__(self):
        return self.title

class Reward(models.Model):
    student_name = models.CharField(max_length=200)
    student_department = models.CharField(max_length=100)
    student_batch = models.CharField(max_length=10)
    achievement = models.TextField()
    image = models.ImageField(upload_to='rewards/', blank=True, null=True)  
    awarded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, related_name='reward_likes', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def total_likes(self):
        return self.likes.count()
    
    def __str__(self):
        return f"{self.student_name} - {self.achievement[:50]}"

class Document(models.Model):
    DOCUMENT_TYPE_CHOICES = (
        ('exam', 'Exam Paper'),
        ('research', 'Research Paper'),
        ('project', 'Project'),
        ('book', 'Book'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    file = models.FileField(
        upload_to='documents/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'ppt', 'pptx'])]
    )
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, related_name='document_likes', blank=True)
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = DocumentManager()
    
    def total_likes(self):
        return self.likes.count()
    
    def __str__(self):
        return self.title

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by {self.user} on {self.created_at}"
    
    # Add this method to get the content object
    @property
    def content_object(self):
        return self.content_type.get_object_for_this_type(id=self.object_id)

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Generic foreign key approach
    content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    
    class Meta:
        unique_together = ['user', 'content_type', 'object_id']
    
    def __str__(self):
        return f"Like by {self.user}"

class RepresentativeRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    request_message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_requests')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    admin_notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Representative Request - {self.user} ({self.status})"

class FeaturedPhoto(models.Model):
    photo = models.OneToOneField(Photo, on_delete=models.CASCADE)
    featured_from = models.DateTimeField(auto_now_add=True)
    featured_until = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Featured: {self.photo.title}"