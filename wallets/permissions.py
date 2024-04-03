from rest_framework import permissions

class IsOwnerOrCoOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners or co-owners of an object to read, update it.
    """

    def has_object_permission(self, request, view, obj):
        """
        Return True if permission is granted to the wallet owner or co-owner.
        """
        return obj.owner == request.user or obj.co_owner == request.user