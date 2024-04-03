from django.contrib.auth.models import User

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.reverse import reverse 
from rest_framework import  permissions, viewsets

from .models import Wallet
from .serializers import WalletSerializer, UserSerializer
from .permissions import IsOwnerOrCoOwner
    
@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'users': reverse('user-list', request=request, format=format),
        'wallets': reverse('wallets-list', request=request, format=format)
    })
    
class UserList(ListAPIView):
    """
    List all users.
    
    This view returns a list of all the users in the system.
    
    Attributes:
        queryset: A queryset that retrieves all the users from the database.
        serializer_class: A UserSerializer instance that serializes the users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(RetrieveAPIView):
    """
    Retrieve a user.

    This view retrieves a specific user from the database.

    Attributes:
        queryset: A queryset that retrieves all the users from the database.
        serializer_class: A UserSerializer instance that serializes the user.
        permission_classes: A list of permission classes that determine who can access this view.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsOwnerOrCoOwner]


class WalletViewSet(viewsets.ModelViewSet):
    """
    Viewset for Wallet model.
    
    This viewset provides CRUD operations for the Wallet model.

    Attributes:
        queryset: A queryset that retrieves all the wallets from the database.
        serializer_class: A WalletSerializer instance that serializes the wallets.
        permission_classes: A list of permission classes that determine who can access this view.

    Methods:
        perform_create: Creates a new wallet instance and associates it with the current user.
    """

    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

