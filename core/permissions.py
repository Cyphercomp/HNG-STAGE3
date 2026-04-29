# authentication/permissions.py
from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit/create.
    Analysts and Admins can both read.
    """
    def has_permission(self, request, view):
        # 1. User must be authenticated and active
        if not request.user or not request.user.is_authenticated:
            return False

        # 2. Allow GET, HEAD, OPTIONS for all roles
        if request.method in permissions.SAFE_METHODS:
            return True

        # 3. Restrict POST, PUT, PATCH, DELETE to Admin only
        return request.user.role == 'admin'