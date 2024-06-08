from rest_framework import permissions


class IsOwnerOrCoOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners or co-owners of an object to read, update it.
    """

    def has_object_permission(self, request, view, obj):
        """
        Return True if permission is granted to the object owner or co-owners.
        """

        return (
            int(obj["owner_id"]) == request.user.id
            or request.user.id in obj["co_owners"]
            or request.user.is_staff
        )


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to read, update it.
    """

    def has_object_permission(self, request, view, obj):
        """
        Return True if permission is granted to the object owner.
        """

        return int(obj["owner_id"]) == request.user.id
