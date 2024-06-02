from typing import Type
from rest_framework.request import Request
from django.db.models import Model
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import Http404

class HandlersChecks:

    @staticmethod
    def check_ownership(request: Request, object_class: Type[Model], instance_id: int) -> None:
        """
        Check if the user has permission to perform an action on an instance of a model.

        Args:
            request (Request): The request.
            object_class (Type[Model]): The model class.
            instance_id (int): The id of the instance.

        Raises:
            PermissionDenied: If the user does not have permission to perform the action.
        
        """

        instance = object_class.objects.get(id=instance_id)

        if not request.user.is_staff and instance.owner != request.user and request.user not in instance.co_owners.all():
            raise PermissionDenied(f"You do not have permission to perform this action on this {object_class.__name__}.")

    @staticmethod
    def check_if_exists(object_class: Type[Model], instance_id: int) -> None:
        """
        Check if an instance of a model exists.

        Args:
            object_class (Type[Model): The model class.
            instance_id (int): The id of the instance.

        Raises:
            Http404: If the instance does not exist.
        """
        
        try:
            object_class.objects.get(id=instance_id)

        except ObjectDoesNotExist:
            raise Http404
