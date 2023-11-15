"""
Permission for profile app
"""
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Makes sure a user has appropriate permission
    to perform a task
    """
    def has_object_permission(self, request, view, obj):
        """
        Checks for the user permission
        """
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.user == request.user
