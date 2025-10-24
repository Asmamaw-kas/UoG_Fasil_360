from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Check if the object has an 'uploaded_by' or 'user' attribute
        if hasattr(obj, 'uploaded_by'):
            return obj.uploaded_by == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'awarded_by'):
            return obj.awarded_by == request.user
        
        return False

class IsRepresentative(permissions.BasePermission):
    """
    Permission to only allow representatives to access.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_representative

class IsAdminOrRepresentative(permissions.BasePermission):
    """
    Permission to allow both admin and representatives.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_staff or request.user.is_representative
        )