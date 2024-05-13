from django.contrib.auth.models import User
from django.db.models import Sum
from django.core.exceptions import ValidationError, FieldError
from django.core.exceptions import PermissionDenied
from django.http import Http404

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.reverse import reverse 
from rest_framework import  permissions, viewsets

from .models import Wallet, Account, Deposit, MarketAssetTransaction, TreasuryBondsTransaction, Withdrawal, UserAsset, UserTreasuryBonds
from .serializers import WalletSerializer, WalletCreateSerializer, UserSerializer, AccountSerializer, AccountCreateSerializer, DepositSerializer, DepositCreateSerializer, MarketAssetTransactionCreateSerializer, MarketAssetTransactionSerializer, WithdrawalSerializer, WithdrawalCreateSerializer, TreasuryBondsTransactionCreateSerializer, TreasuryBondsTransactionSerializer
from .serializers import UserDetailedAssetSerializer, UserSimpleAssetSerializer, UserDetailedTreasuryBondsSerializer, UserSimpleTreasuryBondsSerializer

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
        
        account = serializer.save(owner=self.request.user)
        account.save()

    def get_serializer_class(self):
        
        if self.request.method == 'POST' or self.request.method == 'PUT':
            return AccountCreateSerializer
        return AccountSerializer
    

class DepositViewSet(viewsets.ModelViewSet):
    """
    Viewset for Deposit model.
    
    This viewset provides CRUD operations for the Deposit model.

    Attributes:
        queryset: A queryset that retrieves all the deposits from the database.
        permission_classes: A list of permission classes that determine who can access this view.
    """

    queryset = Deposit.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        
        if self.action == 'list':
            self.permission_classes = [permissions.IsAdminUser]
        elif self.action == 'create':
            self.permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['retrieve', 'update']:
            self.permission_classes = [IsOwnerOrCoOwner]
        elif self.action == 'destroy':
            self.permission_classes = [IsOwner]
        return super(DepositViewSet, self).get_permissions()

    def perform_create(self, serializer):
        
        deposit = serializer.save(user=self.request.user)
    
    def get_serializer_class(self):
        
        if self.request.method == 'POST' or self.request.method == 'PUT':
            return DepositCreateSerializer
        return DepositSerializer
    
class WithdrawalViewSet(viewsets.ModelViewSet):
    """
    Viewset for Withdrawal model.
    
    This viewset provides CRUD operations for the Withdrawal model.

    Attributes:
        queryset: A queryset that retrieves all the withdrawals from the database.
        permission_classes: A list of permission classes that determine who can access this view.
    """

    queryset = Withdrawal.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        
        if self.action == 'list':
            self.permission_classes = [permissions.IsAdminUser]
        elif self.action == 'create':
            self.permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['retrieve', 'update']:
            self.permission_classes = [IsOwnerOrCoOwner]
        elif self.action == 'destroy':
            self.permission_classes = [IsOwner]
        return super(WithdrawalViewSet, self).get_permissions()

    def perform_create(self, serializer):
        
        withdrawal = serializer.save(user=self.request.user)
    
    def get_serializer_class(self):
        
        if self.request.method == 'POST' or self.request.method == 'PUT':
            return WithdrawalCreateSerializer
        return WithdrawalSerializer

class MarketAssetTransactionViewSet(viewsets.ModelViewSet):
    """
    Viewset for Transaction model.
    
    This viewset provides CRUD operations for the Transaction model.

    Attributes:
        queryset: A queryset that retrieves all the transactions from the database.
        permission_classes: A list of permission classes that determine who can access this view.
    """

    queryset = MarketAssetTransaction.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        
        if self.action == 'list':
            self.permission_classes = [permissions.IsAdminUser]
        elif self.action == 'create':
            self.permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['retrieve', 'update']:
            self.permission_classes = [IsOwnerOrCoOwner]
        elif self.action == 'destroy':
            self.permission_classes = [IsOwner]
        return super(MarketAssetTransactionViewSet, self).get_permissions()

    def perform_create(self, serializer):
        
        transaction = serializer.save(user=self.request.user)
    
    def get_serializer_class(self):
        
        if self.request.method == 'POST' or self.request.method == 'PUT':
            return MarketAssetTransactionCreateSerializer
        return MarketAssetTransactionSerializer
    
class TreasuryBondsTransactionViewSet(viewsets.ModelViewSet):
    """
    Viewset for Transaction model.
    
    This viewset provides CRUD operations for the Transaction model.

    Attributes:
        queryset: A queryset that retrieves all the transactions from the database.
        permission_classes: A list of permission classes that determine who can access this view.
    """

    queryset = TreasuryBondsTransaction.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        
        if self.action == 'list':
            self.permission_classes = [permissions.IsAdminUser]
        elif self.action == 'create':
            self.permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['retrieve', 'update']:
            self.permission_classes = [IsOwnerOrCoOwner]
        elif self.action == 'destroy':
            self.permission_classes = [IsOwner]
        return super(TreasuryBondsTransactionViewSet, self).get_permissions()

    def perform_create(self, serializer):
        
        transaction = serializer.save(user=self.request.user)
    
    def get_serializer_class(self):
        
        if self.request.method == 'POST' or self.request.method == 'PUT':
            return TreasuryBondsTransactionCreateSerializer
        return TreasuryBondsTransactionSerializer
    

class ObjectDependeciesList(ListAPIView):

    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        
        if 'account_id' in self.kwargs:
            account_id = self.kwargs['account_id']
            queryset = self.object_class.objects.filter(account=account_id)
            
            try:
                account = Account.objects.get(id=self.kwargs['account_id'])
            except Account.DoesNotExist:
                raise Http404({'account':'Account does not exist.'})
            
            if self.request.user != account.owner and self.request.user not in account.co_owners.all():
                raise PermissionDenied('You do not have permission to view these transactions.')
            
        elif 'wallet_id' in self.kwargs:
            wallet_id = self.kwargs['wallet_id']
            queryset = self.object_class.objects.filter(wallet=wallet_id)
            
            try:
                wallet = Wallet.objects.get(id=self.kwargs['wallet_id'])
            except Wallet.DoesNotExist:
                raise Http404({'wallet':'Wallet does not exist.'})
            
            if self.request.user != wallet.owner and self.request.user not in wallet.co_owners.all():
                raise PermissionDenied('You do not have permission to view these transactions.')
            
        elif 'user_id' in self.kwargs:
            user_id = self.kwargs['user_id']
            queryset = self.object_class.objects.filter(user=user_id)
            
            try:
                user = User.objects.get(id=self.kwargs['user_id'])
            except User.DoesNotExist:
                raise Http404({'user':'User does not exist.'})
            
            if self.request.user != user:
                raise PermissionDenied('You do not have permission to view these transactions.')
            
        return queryset


class ObjectTreasuryBondsTransactionsList(ObjectDependeciesList):

    serializer_class = TreasuryBondsTransactionSerializer
    object_class = TreasuryBondsTransaction
    
    def get_queryset(self):
        
        params = self.request.query_params
        queryset = super().get_queryset()
        
        for param in params:
            
            try:
                if param == 'currency':
                    queryset = queryset.filter(currency__code=params[param])
                    continue
                elif param == 'after':
                    queryset = queryset.filter(transaction_date__gte=params[param])
                    continue
                elif param == 'before':
                    queryset = queryset.filter(transaction_date__lte=params[param])
                    continue
                else:
                    queryset = queryset.filter(**{param: params[param]})
            except FieldError:
                pass
        
        return queryset    

class ObjectMarketTransactionsList(ObjectDependeciesList):

    serializer_class = MarketAssetTransactionSerializer
    object_class = MarketAssetTransaction
   
    def get_queryset(self):

        params = self.request.query_params
        queryset = super().get_queryset()
        
        for param in params:

            try:
                if param == 'currency':
                    queryset = queryset.filter(currency__code=params[param])
                    continue
                elif param == 'after':
                    queryset = queryset.filter(transaction_date__gte=params[param])
                    continue
                elif param == 'before':
                    queryset = queryset.filter(transaction_date__lte=params[param])
                    continue
                else:
                    queryset = queryset.filter(**{param: params[param]})
            except FieldError:
                pass

        return queryset
    

class ObjectUserAssetsList(ObjectDependeciesList):

    serializer_class = UserDetailedAssetSerializer
    object_class = UserAsset

    def get_serializer_class(self):
    
        if "detailed" in self.request.query_params:
            return UserDetailedAssetSerializer
        else:
            return UserSimpleAssetSerializer
    
    def get_queryset(self):

        params = self.request.query_params
        queryset = super().get_queryset()

        if "all" not in params:
            queryset = queryset.filter(active=True)
        
        for param in params:
            try:
                if param == 'currency':
                    queryset = queryset.filter(currency__code=params[param])
                    continue
                else:
                    queryset = queryset.filter(**{param: params[param]})
            except FieldError:
                pass

        if 'detailed' not in params:
            queryset = queryset.values('asset').annotate(amount=Sum('amount'))
        


        return queryset
    
class ObjectUserTreasuryBondsList(ObjectDependeciesList):


    serializer_class = UserDetailedTreasuryBondsSerializer
    object_class = UserTreasuryBonds

    def get_serializer_class(self):
    
        if "detailed" in self.request.query_params:
            return UserDetailedTreasuryBondsSerializer
        else:
            return UserSimpleTreasuryBondsSerializer
    
    def get_queryset(self):

        params = self.request.query_params
        queryset = super().get_queryset()

        if "all" not in params:
            queryset = queryset.filter(active=True)
        
        for param in params:
            try:
                queryset = queryset.filter(**{param: params[param]})
            except FieldError:
                pass

        if 'detailed' not in params:
            queryset = queryset.values('bond').annotate(amount=Sum('amount'))
        
        return queryset

from django.http import HttpResponse

def AccountTest(account_id):

    account = Account.objects.get(id=1)
    suma = 0
    for asset in account.assets.filter(active=True):
        
        print(asset.total_price, asset.current_value)
        suma = suma + asset.current_value

    print(suma) 
    print(account)
    return HttpResponse('Hello, World!')





