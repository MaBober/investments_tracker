from rest_framework import permissions

class IsOwnerOrCoOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners or co-owners of an object to read, update it.
    """

    def has_object_permission(self, request, view, obj):
        """
        Return True if permission is granted to the wallet owner or is on the co-owner list.
        """
        try:
            return obj.owner == request.user or request.user in obj.co_owners.all()
        except AttributeError:
            return obj.wallet.owner == request.user or request.user in obj.wallet.co_owners.all()
           
    
class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to read, update it.
    """

    def has_object_permission(self, request, view, obj):
        """
        Return True if permission is granted to the wallet owner.
        """
        try:
            return obj.owner == request.user
        except AttributeError:
            return obj.user == request.user
    
    