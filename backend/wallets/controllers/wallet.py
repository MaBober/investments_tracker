from wallets.models import Wallet
from wallets.repository import WalletRepository
from wallets.schema import (
    BuildWalletRequest,
    BuildWalletResponse,
    ListWalletsRequest,
    ListWalletsResponse,
    WalletDetailsRequest,
    WalletDetailsResponse,
    DeleteWalletResponse,
    DeleteWalletRequest,
    UpdateWalletRequest,
    UpdateWalletResponse
)


class WalletController:
    """
    Controller for the Wallet model.
    
    This controller contains all logic for the Wallet model. It uses the WalletRepository to access the database.
    """

    @staticmethod
    def build_wallet(request: BuildWalletRequest) -> BuildWalletResponse:
        """
        Create a wallet instance from the request data by accessing the repository.

        Args:
            request (BuildWalletRequest): The request object.

        Returns:
            BuildWalletResponse: The response object.
        """
        co_owners = request.data.pop('co_owners', [])
        wallet = WalletRepository.create_wallet(
            request_data=request.data,
            owner=request.owner
        )

        if co_owners:
            WalletRepository.add_co_owners_to_wallet(
                wallet=wallet,
                co_owners=co_owners
            )

        response = BuildWalletResponse(wallet)
            
        return response

    @staticmethod
    def list_wallets(request: ListWalletsRequest) -> ListWalletsResponse:
        """
        List all wallets by accessing the repository.

        Args:
            request (ListWalletsRequest): The request object.

        Returns:
            ListWalletsResponse: The response object.
        """

        if not request.user.is_staff:
            request.parameters['user_id'] = request.user.id

        wallets = WalletRepository.get_all_wallets(
            user_id=request.parameters.get('user_id'),
            co_owner_id=request.parameters.get('co_owner_id'),
            owner_id=request.parameters.get('owner_id'),
            created_before=request.parameters.get('created_before'),
            created_after=request.parameters.get('created_after')
        )

        response = ListWalletsResponse(wallets)

        return response

    @staticmethod
    def wallet_details(request: WalletDetailsRequest) -> Wallet:
        """
        Get the details of a wallet by accessing the repository.

        Args:
            wallet_id (int): The wallet id.

        Returns:
            Wallet: The wallet instance.
        """

        wallet = WalletRepository.get_single_wallet(request.pk)
        response = WalletDetailsResponse(wallet)

        return response

    @staticmethod
    def update_wallet(request: UpdateWalletRequest) -> UpdateWalletResponse:
        """
        Request to update a wallet by accessing the repository.

        Args:
            wallet_id (int): The wallet id.

        Returns:
            Wallet: The wallet instance.
        """

        co_owners = request._data.pop('co_owners', [])
        wallet = WalletRepository.get_single_wallet(request.pk)

        for key, value in request.data.items():
            setattr(wallet, key, value)

        WalletRepository.save_wallet(wallet)

        if co_owners:
            WalletRepository.add_co_owners_to_wallet(wallet, co_owners)
        
        else:
            WalletRepository.erase_co_owners_from_wallet(wallet)

        response = UpdateWalletResponse(wallet)

        return response

    @staticmethod
    def delete_wallet(request: DeleteWalletRequest) -> DeleteWalletResponse:
        """
        Request to delete a wallet by accessing the repository.

        Args:
            wallet_id (int): The wallet id.

        Returns:
            None
        """

        wallet = WalletRepository.get_single_wallet(request.pk)
        WalletRepository.delete_wallet(wallet)

        response = DeleteWalletResponse()

        return response
