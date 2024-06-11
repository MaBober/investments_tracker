from django.http import Http404

from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView

from wallets.controllers import WalletController
from wallets.serializers.wallet import (
    WalletCreateSerializer,
    WalletListParametersSerializer,
)
from wallets.permissions import IsOwnerOrCoOwner, IsOwner
from wallets.schema import (
    BuildWalletRequest,
    BuildWalletResponse,
    ListWalletsRequest,
    ListWalletsResponse,
    WalletDetailsRequest,
    WalletDetailsResponse,
    DeleteWalletRequest,
    DeleteWalletResponse,
    UpdateWalletRequest,
    UpdateWalletResponse,
)


class WalletView(APIView):
    """
    Handle the GET and POST requests for the Wallet model.
    """

    def get(self, request: Request) -> Response:

        request_parameters_serializer = WalletListParametersSerializer(
            data=request.query_params
        )
        request_parameters_serializer.is_valid(raise_exception=True)

        request = ListWalletsRequest(
            query_parameters=request_parameters_serializer.validated_data,
            user=request.user,
        )
        wallets: ListWalletsResponse = WalletController.list_wallets(request)

        wallets = WalletController.list_wallets(request)

        return Response(data=wallets.data, status=wallets.status)

    def post(self, request: Request) -> Response:

        serializer = WalletCreateSerializer(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():

            request = BuildWalletRequest(
                request_data=serializer.validated_data, owner=request.user
            )
            wallet: BuildWalletResponse = WalletController.build_wallet(request)

            return Response(
                data=wallet.data,
                status=wallet.status,
                headers={"Location": wallet.location},
            )

        return Response(serializer.errors, status=400)


class WalletDetailView(APIView):
    """
    Handle the GET, PATCH and DELETE requests for the Wallet model.
    """

    def get_permissions(self):

        if self.request.method == "DELETE":
            self.permission_classes = [IsOwner]
        else:
            self.permission_classes = [IsOwnerOrCoOwner]

        return super(WalletDetailView, self).get_permissions()

    def get_wallet_and_check_permissions(self, request, pk):

        controller_request = WalletDetailsRequest(pk)
        wallet: WalletDetailsResponse = WalletController.wallet_details(
            controller_request
        )

        if not wallet.data:
            raise Http404("Wallet not found.")

        self.check_object_permissions(request, wallet.data)

        return wallet

    def get(self, request: Request, pk: int) -> Response:

        wallet = self.get_wallet_and_check_permissions(request, pk)

        return Response(data=wallet.data, status=wallet.status)

    def patch(self, request: Request, pk: int) -> Response:

        self.get_wallet_and_check_permissions(request, pk)
        serializer = WalletCreateSerializer(
            data=request.data, context={"request": request}, partial=True
        )

        if serializer.is_valid():
            controller_request = UpdateWalletRequest(pk, serializer.validated_data)
            response: UpdateWalletResponse = WalletController.update_wallet(
                controller_request
            )

            return Response(data=response.data, status=response.status)

        return Response(serializer.errors, status=400)

    def delete(self, request: Request, pk: int) -> Response:

        self.get_wallet_and_check_permissions(request, pk)

        controller_request = DeleteWalletRequest(pk)
        response: DeleteWalletResponse = WalletController.delete_wallet(
            controller_request
        )

        return Response(
            data={"id": pk, "message": "Wallet deleted."}, status=response.status
        )
