from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request

from django.http import HttpResponseNotAllowed

from wallets.models import Wallet
from wallets.controllers import WalletController
from wallets.serializers.wallet import WalletCreateSerializer, WalletSerializer
from wallets.utilities import HandlersChecks


class WalletHandler:

    model_class = Wallet

    @staticmethod
    @api_view(['GET', 'POST'])
    def WalletView(request):
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
    def WalletDetailView(request, pk):

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

        




    