
from django.http import Http404

from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView

from wallets.controllers import WalletController
from wallets.serializers.wallet import WalletCreateSerializer, WalletSerializer, WalletListParametersSerializer
from wallets.permissions import IsOwnerOrCoOwner, IsOwner


class WalletView(APIView):
    """
    Handle the GET and POST requests for the Wallet model.
    """

    def get(self, request: Request) -> Response:
            
            request_parameters_serializer = WalletListParametersSerializer(data=request.query_params)
            request_parameters_serializer.is_valid(raise_exception=True)

            wallets = WalletController.list_wallets(request)
            return Response(WalletSerializer(wallets, many=True).data, status=200)
    
    def post(self, request: Request) -> Response:
            
            serializer = WalletCreateSerializer(data=request.data, context={'request': request})
    
            if serializer.is_valid():
    
                wallet = WalletController.build_wallet(request.data, request.user)
                return Response(WalletCreateSerializer(wallet).data, status=201)
            
            return Response(serializer.errors, status=400)


class WalletDetailView(APIView):
    """
    Handle the GET, PATCH and DELETE requests for the Wallet model.
    """
    
    def get_permissions(self):

        if self.request.method == 'DELETE':
            self.permission_classes = [IsOwner]
        else:
            self.permission_classes = [IsOwnerOrCoOwner]    

        return super(WalletDetailView, self).get_permissions()

    def get_wallet_and_check_permissions(self, request, pk):

        wallet = WalletController.wallet_details(pk)

        if not wallet:
            raise Http404('Wallet not found.')
        
        self.check_object_permissions(request, wallet)

        return wallet
    
    def get(self, request: Request, pk: int) -> Response:

        wallet = self.get_wallet_and_check_permissions(request, pk)
        return Response(WalletSerializer(wallet).data, status=200)
        
    def patch(self, request: Request, pk: int) -> Response:

        self.get_wallet_and_check_permissions(request, pk)
        serializer = WalletCreateSerializer(data=request.data, context={'request': request}, partial=True)

        if serializer.is_valid():
            wallet = WalletController.update_wallet(pk, request.data)
            return Response(WalletSerializer(wallet).data, status=200)
        
        return Response(serializer.errors, status=400)
        
    def delete(self, request: Request, pk: int) -> Response:

        self.get_wallet_and_check_permissions(request, pk)
        WalletController.delete_wallet(pk)

        return Response({'id': pk, 'message': 'Wallet deleted.'}, status=200)


        

        




    