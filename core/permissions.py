from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission pour permettre uniquement aux propriétaires de modifier l'objet
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.utilisateur == request.user

class IsAnnonceurOrAdmin(permissions.BasePermission):
    """
    Permission pour restreindre l'accès aux annonceurs et admins
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role in ['ANNONCEUR', 'ADMIN'] or 
            request.user.is_superuser
        ) 