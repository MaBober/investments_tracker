from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView

from django.http import HttpResponseNotAllowed

from wallets.models import Wallet
from wallets.controllers import WalletController
from wallets.serializers.wallet import WalletCreateSerializer, WalletSerializer
from wallets.utilities import HandlersChecks


class WalletView(APIView):
    """
    Handle the GET and POST requests for the Wallet model.
    """

    def get(self, request: Request) -> Response:

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

    def get(self, request: Request, pk: int) -> Response:

        wallet = WalletController.wallet_details(pk)
        return Response(WalletSerializer(wallet).data, status=200)
        
    def patch(self, request: Request, pk: int) -> Response:
         
        serializer = WalletCreateSerializer(data=request.data, context={'request': request}, partial=True)

        if serializer.is_valid():
            wallet = WalletController.update_wallet(pk, request.data)
            return Response(WalletSerializer(wallet).data, status=200)
        
        return Response(serializer.errors, status=400)

        
    def delete(self, request: Request, pk: int) -> Response:

        WalletController.delete_wallet(pk)
        return Response({'id': pk, 'message': 'Wallet deleted.'}, status=200)
        

        




    