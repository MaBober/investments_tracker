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
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsOwnerOrCoOwner]


class WalletViewSet(viewsets.ModelViewSet):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

