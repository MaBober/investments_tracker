from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.reverse import reverse 
from rest_framework import  permissions, viewsets

from .models import Wallet, Account
from .serializers import WalletSerializer, WalletCreateSerializer, UserSerializer, AccountSerializer, AccountCreateSerializer
from .permissions import IsOwnerOrCoOwner, IsOwner
    
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
        permission_classes: A list of permission classes that determine who can access this view.

    Methods:
        perform_create: Creates a new wallet instance and associates it with the current user.
        get_serializer_class: Returns the appropriate serializer class based on the request method.
    """

    queryset = Wallet.objects.all()
    permission_classes = [permissions.IsAdminUser, IsOwnerOrCoOwner, permissions.IsAuthenticated, IsOwner]

    def get_permissions(self):
        if self.action == 'list':
            self.permission_classes = [permissions.IsAdminUser]
        elif self.action == 'create':
            self.permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['retrieve', 'update']:
            self.permission_classes = [IsOwnerOrCoOwner]
        elif self.action == 'destroy':
            self.permission_classes = [IsOwner]
        return super(WalletViewSet, self).get_permissions()

    def perform_create(self, serializer):

        wallet = serializer.save(owner=self.request.user)
        wallet.save()

    def get_serializer_class(self):

        if self.request.method == 'POST' or self.request.method == 'PUT':
            return WalletCreateSerializer
        return WalletSerializer
    

class AccountViewSet(viewsets.ModelViewSet):
    """
    Viewset for Account model.
    
    This viewset provides CRUD operations for the Account model.

    Attributes:
        queryset: A queryset that retrieves all the accounts from the database.
        permission_classes: A list of permission classes that determine who can access this view.
    
    Methods:
        perform_create: Creates a new account instance and associates it with the current user.
        get_serializer_class: Returns the appropriate serializer class based on the request method.
    """

    queryset = Account.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        print("get_permissions")
        if self.action == 'list':
            self.permission_classes = [permissions.IsAdminUser]
        elif self.action == 'create':
            self.permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['retrieve', 'update']:
            self.permission_classes = [IsOwnerOrCoOwner]
        elif self.action == 'destroy':
            self.permission_classes = [IsOwner]
        return super(AccountViewSet, self).get_permissions()

    def perform_create(self, serializer):
        
        print("perform_create")
        account = serializer.save(owner=self.request.user)
        account.save()

    def get_serializer_class(self):
        
        print("get_serializer_class")
        if self.request.method == 'POST' or self.request.method == 'PUT':
            print("AccountCreateSerializer")
            return AccountCreateSerializer
        return AccountSerializer