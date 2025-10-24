from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.contenttypes.models import ContentType
from .models import (
    User, Category, Photo, Reward, Document, 
    Comment, Like, RepresentativeRequest, FeaturedPhoto
)

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'first_name', 
                 'last_name', 'department', 'campus', 'batch']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('Account disabled')
            attrs['user'] = user
            return attrs
        raise serializers.ValidationError('Must include email and password')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'department', 'campus', 'batch', 'user_type', 
                 'is_representative', 'is_verified', 'date_joined']
        read_only_fields = ['id', 'date_joined']

class CategorySerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'batch_specific', 'batch', 
                 'created_by', 'created_by_name', 'created_at']
        read_only_fields = ['id', 'created_by', 'created_at']

class PhotoSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    total_likes = serializers.SerializerMethodField()
    user_has_liked = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    comments_count = serializers.SerializerMethodField()  
    
    class Meta:
        model = Photo
        fields = ['id', 'title', 'description', 'image', 'category', 'category_name',
                 'photo_type', 'uploaded_by', 'uploaded_by_name', 'likes',
                 'total_likes', 'user_has_liked', 'is_featured', 'is_approved',
                 'comments_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'uploaded_by', 'created_at', 'updated_at', 'likes']
    
    def get_total_likes(self, obj):
        return obj.total_likes()
    
    def get_user_has_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False
    
    def get_comments_count(self, obj):
        return Comment.objects.filter(
            content_type=ContentType.objects.get_for_model(obj),
            object_id=obj.id
        ).count()
    
    def create(self, validated_data):
        validated_data['uploaded_by'] = self.context['request'].user
        return super().create(validated_data)

class RewardSerializer(serializers.ModelSerializer):
    awarded_by_name = serializers.CharField(source='awarded_by.get_full_name', read_only=True)
    total_likes = serializers.SerializerMethodField()
    user_has_liked = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Reward
        fields = ['id', 'student_name', 'student_department', 'student_batch',
                 'achievement', 'image', 'image_url', 'awarded_by', 
                 'awarded_by_name', 'likes', 'total_likes', 'user_has_liked',
                 'comments_count', 'created_at']
        read_only_fields = ['id', 'awarded_by', 'created_at', 'likes']
    
    def get_total_likes(self, obj):
        return obj.total_likes()
    
    def get_user_has_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False
    
    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None
    
    def get_comments_count(self, obj):
        return Comment.objects.filter(
            content_type=ContentType.objects.get_for_model(obj),
            object_id=obj.id
        ).count()
    
    def create(self, validated_data):
        validated_data['awarded_by'] = self.context['request'].user
        return super().create(validated_data)

class DocumentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    total_likes = serializers.SerializerMethodField()
    user_has_liked = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = ['id', 'title', 'description', 'document_type', 'file',
                 'uploaded_by', 'uploaded_by_name', 'likes', 'total_likes',
                 'user_has_liked', 'is_approved', 'comments_count',
                 'created_at', 'updated_at']
        read_only_fields = ['id', 'uploaded_by', 'created_at', 'updated_at', 'likes']
    
    def get_total_likes(self, obj):
        return obj.total_likes()
    
    def get_user_has_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False
    
    def get_comments_count(self, obj):
        return Comment.objects.filter(
            content_type=ContentType.objects.get_for_model(obj),
            object_id=obj.id
        ).count()
    
    def create(self, validated_data):
        validated_data['uploaded_by'] = self.context['request'].user
        return super().create(validated_data)

class CommentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_batch = serializers.CharField(source='user.batch', read_only=True)
    user_first_name = serializers.CharField(source='user.first_name', read_only=True)
    user_last_name = serializers.CharField(source='user.last_name', read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'user', 'user_name', 'user_first_name', 'user_last_name', 'user_batch', 'content', 
                 'content_type', 'object_id', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'user', 'content_type', 'object_id', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

class RepresentativeRequestSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_batch = serializers.CharField(source='user.batch', read_only=True)
    user_department = serializers.CharField(source='user.department', read_only=True)
    
    class Meta:
        model = RepresentativeRequest
        fields = ['id', 'user', 'user_name', 'user_batch', 'user_department',
                 'request_message', 'status', 'created_at', 'reviewed_by',
                 'reviewed_at', 'admin_notes']
        read_only_fields = ['id', 'user', 'created_at', 'reviewed_by', 'reviewed_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class FeaturedPhotoSerializer(serializers.ModelSerializer):
    photo_details = PhotoSerializer(source='photo', read_only=True)
    
    class Meta:
        model = FeaturedPhoto
        fields = ['id', 'photo', 'photo_details', 'featured_from', 
                 'featured_until', 'is_active']