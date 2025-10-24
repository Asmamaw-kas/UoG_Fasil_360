from rest_framework import viewsets, status, filters
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, Count
from django.apps import apps
from .models import (
    User, Category, Photo, Reward, Document, Comment, 
    Like, RepresentativeRequest, FeaturedPhoto
)
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserSerializer,
    CategorySerializer, PhotoSerializer, RewardSerializer, DocumentSerializer,
    CommentSerializer, LikeSerializer, RepresentativeRequestSerializer,
    FeaturedPhotoSerializer
)
from .permissions import IsOwnerOrReadOnly, IsRepresentative, IsAdminOrRepresentative

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate tokens for newly registered user
            refresh = RefreshToken.for_user(user)
            user_data = UserSerializer(user, context=self.get_serializer_context()).data
            
            return Response({
                'user': user_data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            user_data = UserSerializer(user, context=self.get_serializer_context()).data
            
            return Response({
                'user': user_data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def profile(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['batch_specific', 'batch']
    search_fields = ['name', 'description']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [IsAdminOrRepresentative()]
        return [AllowAny()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Categories are always visible to everyone
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class PhotoViewSet(viewsets.ModelViewSet):
    queryset = Photo.objects.all().order_by('-created_at')
    serializer_class = PhotoSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'photo_type', 'is_featured', 'is_approved', 'uploaded_by']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'total_likes']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [IsAuthenticated(), IsOwnerOrReadOnly()]
        return [AllowAny()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # For list view, show only approved photos to non-authenticated users
        if self.action == 'list' and not self.request.user.is_authenticated:
            queryset = queryset.filter(is_approved=True)
        
        # For authenticated non-staff users, show their own unapproved photos + all approved
        elif self.action == 'list' and self.request.user.is_authenticated and not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(is_approved=True) | 
                Q(uploaded_by=self.request.user)
            )
        
        # Filter by batch if specified
        batch = self.request.query_params.get('batch')
        if batch:
            queryset = queryset.filter(category__batch=batch)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        photo = self.get_object()
        user = request.user
        
        if photo.likes.filter(id=user.id).exists():
            photo.likes.remove(user)
            message = 'Like removed'
        else:
            photo.likes.add(user)
            message = 'Liked'
        
        # Update featured status based on likes
        if photo.total_likes() >= 10:  # Threshold for featured photos
            photo.is_featured = True
            photo.save()
        
        return Response({'message': message, 'total_likes': photo.total_likes()})
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        featured_photos = self.get_queryset().filter(is_featured=True, is_approved=True)
        page = self.paginate_queryset(featured_photos)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(featured_photos, many=True)
        return Response(serializer.data)
    

class RewardViewSet(viewsets.ModelViewSet):
    queryset = Reward.objects.all().order_by('-created_at')
    serializer_class = RewardSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['student_batch', 'student_department']
    search_fields = ['student_name', 'achievement']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [IsAuthenticated(), IsAdminOrRepresentative()]
        return [AllowAny()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Rewards are always visible to everyone
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(awarded_by=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        reward = self.get_object()
        user = request.user
        
        if reward.likes.filter(id=user.id).exists():
            reward.likes.remove(user)
            message = 'Like removed'
        else:
            reward.likes.add(user)
            message = 'Liked'
        
        return Response({'message': message, 'total_likes': reward.total_likes()})

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all().order_by('-created_at')
    serializer_class = DocumentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['document_type', 'uploaded_by', 'is_approved']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [IsAuthenticated(), IsOwnerOrReadOnly()]
        return [AllowAny()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # For list view, show only approved documents to non-authenticated users
        if self.action == 'list' and not self.request.user.is_authenticated:
            queryset = queryset.filter(is_approved=True)
        
        # For authenticated non-staff users, show their own unapproved documents + all approved
        elif self.action == 'list' and self.request.user.is_authenticated and not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(is_approved=True) | 
                Q(uploaded_by=self.request.user)
            )
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        document = self.get_object()
        user = request.user
        
        if document.likes.filter(id=user.id).exists():
            document.likes.remove(user)
            message = 'Like removed'
        else:
            document.likes.add(user)
            message = 'Liked'
        
        return Response({'message': message, 'total_likes': document.total_likes()})

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['content_type', 'object_id']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        content_type = self.request.query_params.get('content_type')
        object_id = self.request.query_params.get('object_id')
        
        if content_type and object_id:
            try:
                content_type_obj = ContentType.objects.get(model=content_type)
                queryset = queryset.filter(
                    content_type=content_type_obj, 
                    object_id=object_id
                )
            except ContentType.DoesNotExist:
                return Comment.objects.none()
        
        return queryset
    
    def perform_create(self, serializer):
        content_type_str = self.request.data.get('content_type')
        object_id = self.request.data.get('object_id')
        
        try:
            # Handle both string and ID formats for content_type
            if isinstance(content_type_str, str) and content_type_str.isdigit():
                content_type = ContentType.objects.get(id=int(content_type_str))
            elif isinstance(content_type_str, str):
                app_label = apps.get_containing_app_config(__name__).label
                content_type = ContentType.objects.get(app_label=app_label, model=content_type_str.lower())
            else:
                content_type = ContentType.objects.get(id=content_type_str)
            
            # Verify the object exists
            model_class = content_type.model_class()
            content_object = model_class.objects.get(id=object_id)
            
            serializer.save(
                user=self.request.user,
                content_type=content_type,
                object_id=object_id
            )
        except (ContentType.DoesNotExist, model_class.DoesNotExist) as e:
            raise serializers.ValidationError({"error": "Invalid content type or object ID"})

class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class RepresentativeRequestViewSet(viewsets.ModelViewSet):
    queryset = RepresentativeRequest.objects.all().order_by('-created_at')
    serializer_class = RepresentativeRequestSerializer
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return self.queryset
        return self.queryset.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        representative_request = self.get_object()
        representative_request.status = 'approved'
        representative_request.reviewed_by = request.user
        representative_request.save()
        
        # Update user to representative
        user = representative_request.user
        user.is_representative = True
        user.user_type = 'representative'
        user.save()
        
        return Response({'message': 'Request approved successfully'})
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def reject(self, request, pk=None):
        representative_request = self.get_object()
        representative_request.status = 'rejected'
        representative_request.reviewed_by = request.user
        representative_request.save()
        return Response({'message': 'Request rejected'})

class FeaturedPhotoViewSet(viewsets.ModelViewSet):
    queryset = FeaturedPhoto.objects.filter(is_active=True).order_by('-featured_from')
    serializer_class = FeaturedPhotoSerializer
    permission_classes = [IsAdminOrRepresentative]
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def active(self, request):
        active_featured = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(active_featured, many=True)
        return Response(serializer.data)

class SearchViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    
    def list(self, request):
        query = request.query_params.get('q', '')
        category = request.query_params.get('category', '')
        
        results = {}
        
        # Search photos
        photos = Photo.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query),
            is_approved=True
        )
        if category:
            photos = photos.filter(category__name=category)
        results['photos'] = PhotoSerializer(photos, many=True, context={'request': request}).data
        
        # Search rewards
        rewards = Reward.objects.filter(
            Q(student_name__icontains=query) | Q(achievement__icontains=query)
        )
        results['rewards'] = RewardSerializer(rewards, many=True, context={'request': request}).data
        
        # Search documents
        documents = Document.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query),
            is_approved=True
        )
        if category in ['exam', 'research', 'project', 'book']:
            documents = documents.filter(document_type=category)
        results['documents'] = DocumentSerializer(documents, many=True, context={'request': request}).data
        
        return Response(results)