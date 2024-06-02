from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request

from django.http import HttpResponseNotAllowed

from wallets.models import Wallet
from wallets.controllers import WalletController
from wallets.serializers.wallet import WalletCreateSerializer, WalletSerializer
from wallets.utilities import HandlersChecks


class WalletHandler:
    """
    Handler for the Wallet model.

    This handler contains the views for the Wallet model.
    It specifies the methods that should be used to perform actions on the Wallet model,
    when a request is made to the API.

    Attributes:
        model_class: The Wallet model class.

    Methods:
        WalletView: A method that handles the GET and POST requests for the Wallet model.
            It serves request without specific instance.
        WalletDetailView: A method that handles the GET, PATCH and DELETE requests for the Wallet model.
            It serves request with specific instance.

    """

    model_class = Wallet

    @staticmethod
    @api_view(['GET', 'POST'])
    def WalletView(request: Request) -> Response:
        """
        Handle the GET and POST requests for the Wallet model.

        Args:
            request (Request): The request.

        Returns:
            Response: The response for user.
        """
        if request.method == 'GET':

            parameters = request.query_params.dict()

            if not request.user.is_staff:
                parameters['owner_id'] = request.user.id
            
            wallets = WalletController.list_wallets(**parameters)

            return Response(WalletSerializer(wallets, many=True).data, status=200)
            

        elif request.method == 'POST':

            serializer = WalletCreateSerializer(data=request.data, context={'request': request})

            if serializer.is_valid():

                try:
                    wallet = WalletController.build_wallet(request.data, request.user)
                    return Response(WalletCreateSerializer(wallet).data, status=201)
                
                except Exception as e:
                    return Response({'error': str(e)}, status=500)
        
            return Response(serializer.errors, status=400)
        
        else:
            return HttpResponseNotAllowed(['GET', 'POST'])
        
    @api_view(['GET', 'PATCH', 'DELETE'])
    def WalletDetailView(request: Request, pk: int) -> Response:
        """
        Handle the GET, PATCH and DELETE requests for the Wallet model.

        Args:
            request (Request): The request.
            pk (int): The id of the wallet instance.

        Returns:
            Response: The response for user.
        """

        HandlersChecks.check_if_exists(WalletHandler.model_class, pk)
        HandlersChecks.check_ownership(request, WalletHandler.model_class, pk)

        if request.method == 'GET':
            
            try:
                wallet = WalletController.wallet_details(pk)
                return Response(WalletSerializer(wallet).data, status=200)
            
            except Exception as e:
                return Response({'error': str(e)}, status=500)
            
        elif request.method == 'PATCH':

            try:
                serializer = WalletCreateSerializer(data=request.data, context={'request': request}, partial=True)

                if serializer.is_valid():
                    wallet = WalletController.update_wallet(pk, request.data)
                    return Response(WalletSerializer(wallet).data, status=200)
                
                return Response(serializer.errors, status=400)
            
            except Exception as e:
                return Response({'error': str(e)}, status=500)
            
        elif request.method == 'DELETE':

            try:
                wallet = WalletController.delete_wallet(pk)
                return Response({'id': pk, 'message': 'Wallet deleted'}, status=200)
            
            except Exception as e:
                return Response({'error': str(e)}, status=500)

        else:
            return HttpResponseNotAllowed(['GET', 'PUT', 'DELETE'])

        




    