from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import (
    User, Category, Photo, Reward, Document, Comment, 
    Like, RepresentativeRequest, FeaturedPhoto
)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 
                   'department', 'campus', 'batch', 'user_type', 
                   'is_representative', 'is_verified', 'is_staff', 'date_joined')
    list_filter = ('user_type', 'is_representative', 'is_verified', 
                  'department', 'campus', 'batch', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'department')
    ordering = ('-date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Information', {
            'fields': ('user_type', 'department', 'campus', 'batch', 
                      'is_verified', 'is_representative')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Information', {
            'fields': ('user_type', 'department', 'campus', 'batch', 
                      'is_verified', 'is_representative')
        }),
    )
    
    actions = ['make_representative', 'remove_representative']
    
    def make_representative(self, request, queryset):
        updated = queryset.update(is_representative=True, user_type='representative')
        self.message_user(request, f'{updated} users marked as representatives.')
    make_representative.short_description = "Mark selected users as representatives"
    
    def remove_representative(self, request, queryset):
        updated = queryset.update(is_representative=False, user_type='student')
        self.message_user(request, f'{updated} users removed from representatives.')
    remove_representative.short_description = "Remove selected users from representatives"

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'batch_specific', 'batch', 'created_by', 'created_at')
    list_filter = ('batch_specific', 'batch', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at',)
    
    def save_model(self, request, obj, form, change):
        if not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'photo_type', 'uploaded_by', 
                   'total_likes_display', 'is_featured', 'is_approved', 
                   'created_at', 'image_preview')
    list_filter = ('category', 'photo_type', 'is_featured', 'is_approved', 'created_at')
    search_fields = ('title', 'description', 'uploaded_by__username')
    readonly_fields = ('created_at', 'updated_at', 'image_preview')
    list_editable = ('is_featured', 'is_approved')
    actions = ['approve_photos', 'feature_photos', 'unfeature_photos']
    
    def total_likes_display(self, obj):
        return obj.total_likes()
    total_likes_display.short_description = 'Likes'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" style="object-fit: cover;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Preview'
    
    def approve_photos(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} photos approved.')
    approve_photos.short_description = "Approve selected photos"
    
    def feature_photos(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} photos featured.')
    feature_photos.short_description = "Feature selected photos"
    
    def unfeature_photos(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} photos unfeatured.')
    unfeature_photos.short_description = "Unfeature selected photos"

@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'student_department', 'student_batch', 
                   'awarded_by', 'total_likes_display', 'created_at')
    list_filter = ('student_department', 'student_batch', 'created_at')
    search_fields = ('student_name', 'achievement', 'awarded_by__username')
    readonly_fields = ('created_at',)
    
    def total_likes_display(self, obj):
        return obj.total_likes()
    total_likes_display.short_description = 'Likes'

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'document_type', 'uploaded_by', 'file_preview', 
                   'total_likes_display', 'is_approved', 'created_at')
    list_filter = ('document_type', 'is_approved', 'created_at')
    search_fields = ('title', 'description', 'uploaded_by__username')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('is_approved',)
    actions = ['approve_documents']
    
    def total_likes_display(self, obj):
        return obj.total_likes()
    total_likes_display.short_description = 'Likes'
    
    def file_preview(self, obj):
        if obj.file:
            return format_html('<a href="{}" target="_blank">📄 View File</a>', obj.file.url)
        return "No File"
    file_preview.short_description = 'File'
    
    def approve_documents(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} documents approved.')
    approve_documents.short_description = "Approve selected documents"

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'content_preview', 'content_type', 'object_id', 'created_at')
    list_filter = ('content_type', 'created_at')
    search_fields = ('content', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'content_type', 'object_id', 'created_at')
    list_filter = ('content_type', 'created_at')
    search_fields = ('user__username',)
    readonly_fields = ('created_at',)

@admin.register(RepresentativeRequest)
class RepresentativeRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'created_at', 'reviewed_by', 'reviewed_at')
    list_filter = ('status', 'created_at', 'reviewed_at')
    search_fields = ('user__username', 'request_message')
    readonly_fields = ('created_at',)
    actions = ['approve_requests', 'reject_requests']
    
    def approve_requests(self, request, queryset):
        for req in queryset:
            req.status = 'approved'
            req.reviewed_by = request.user
            req.save()
            
            # Update user to representative
            user = req.user
            user.is_representative = True
            user.user_type = 'representative'
            user.save()
        
        self.message_user(request, f'{queryset.count()} requests approved.')
    approve_requests.short_description = "Approve selected requests"
    
    def reject_requests(self, request, queryset):
        updated = queryset.update(status='rejected', reviewed_by=request.user)
        self.message_user(request, f'{updated} requests rejected.')
    reject_requests.short_description = "Reject selected requests"

@admin.register(FeaturedPhoto)
class FeaturedPhotoAdmin(admin.ModelAdmin):
    list_display = ('photo', 'featured_from', 'featured_until', 'is_active')
    list_filter = ('is_active', 'featured_from')
    search_fields = ('photo__title',)
    list_editable = ('is_active',)