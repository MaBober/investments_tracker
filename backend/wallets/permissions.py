from rest_framework import permissions

class IsOwnerOrCoOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners or co-owners of an object to read, update it.
    """

    def has_object_permission(self, request, view, obj):
        """
        Return True if permission is granted to the object owner or co-owners.
        """

        return obj.owner == request.user or request.user in obj.co_owners.all() or request.user.is_staff

    
class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to read, update it.
    """

    def has_object_permission(self, request, view, obj):
        """
        Return True if permission is granted to the object owner.
        """

        return obj.owner == request.user

    
    