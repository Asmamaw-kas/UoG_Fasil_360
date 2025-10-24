from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, CategoryViewSet, PhotoViewSet, RewardViewSet,
    DocumentViewSet, CommentViewSet, LikeViewSet, 
    RepresentativeRequestViewSet, FeaturedPhotoViewSet, SearchViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'photos', PhotoViewSet, basename='photo')
router.register(r'rewards', RewardViewSet, basename='reward')
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'likes', LikeViewSet, basename='like')
router.register(r'representative-requests', RepresentativeRequestViewSet, basename='representativerequest')
router.register(r'featured-photos', FeaturedPhotoViewSet, basename='featuredphoto')
router.register(r'search', SearchViewSet, basename='search')

# Explicit URL patterns for better clarity
urlpatterns = [
    path('', include(router.urls)),
    
    # Additional explicit endpoints
    path('auth/register/', UserViewSet.as_view({'post': 'register'}), name='auth-register'),
    path('auth/login/', UserViewSet.as_view({'post': 'login'}), name='auth-login'),
    path('auth/profile/', UserViewSet.as_view({'get': 'profile'}), name='auth-profile'),
]

# API Root view
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'users': reverse('user-list', request=request, format=format),
        'categories': reverse('category-list', request=request, format=format),
        'photos': reverse('photo-list', request=request, format=format),
        'rewards': reverse('reward-list', request=request, format=format),
        'documents': reverse('document-list', request=request, format=format),
        'comments': reverse('comment-list', request=request, format=format),
        'representative-requests': reverse('representativerequest-list', request=request, format=format),
        'featured-photos': reverse('featuredphoto-list', request=request, format=format),
        'search': reverse('search-list', request=request, format=format),
        'auth-register': reverse('auth-register', request=request, format=format),
        'auth-login': reverse('auth-login', request=request, format=format),
        'auth-profile': reverse('auth-profile', request=request, format=format),
    })

urlpatterns += [
    path('', api_root, name='api-root'),
]