from typing import Type
from rest_framework.request import Request
from django.db.models import Model
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import Http404

class HandlersChecks:

    @staticmethod
    def check_ownership(request: Request, object_class: Type[Model], instance_id: int):

        instance = object_class.objects.get(id=instance_id)

        if not request.user.is_staff and instance.owner != request.user and request.user not in instance.co_owners.all():
            raise PermissionDenied(f"You do not have permission to perform this action on this {object_class.__name__}.")

    @staticmethod
    def check_if_exists(object_class: Type[Model], instance_id: int):

        try:
            object_class.objects.get(id=instance_id)

        except ObjectDoesNotExist:
            raise Http404
