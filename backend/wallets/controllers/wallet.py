from django.db.models.query import QuerySet
from django.contrib.auth.models import User

from rest_framework.request import Request

from wallets.models import Wallet
from wallets.repository import WalletRepository


class WalletController:
    """
    Controller for the Wallet model.
    
    This controller contains all logic for the Wallet model. It uses the WalletRepository to access the database.
    
    Methods:
        build_wallet: A method that creates a wallet instance from the request data by accessing the repository.
        list_wallets: A method that lists all wallets by accessing the repository.
        wallet_details: A method that gets the details of a wallet by accessing the repository.
        update_wallet: A method that updates a wallet by accessing the repository.
        delete_wallet: A method that deletes a wallet by accessing the repository.
    """

    @staticmethod
    def build_wallet(request_data: dict, owner: User) -> Wallet:
        """
        Create a wallet instance from the request data by accessing the repository.

        Args:
            request_data (dict): The request data.
            owner (User): The owner of the wallet.

        Returns:
            Wallet: The wallet instance.
        """
        co_owners = request_data.pop('co_owners', [])
        wallet = WalletRepository.create_wallet(request_data, owner)

        if co_owners:
            WalletRepository.add_co_owners_to_wallet(wallet, co_owners)
            
        return wallet

    @staticmethod
    def list_wallets(request: Request) -> QuerySet[Wallet]:
        """
        List all wallets by accessing the repository.

        Args:
            user (User): The user requesting the wallets.
            **parameters (dict): The query parameters to filter the wallets.

        Returns:
            QuerySet: All listed wallets that match the query parameters.
            
        """

        parameters = request.query_params.dict()

        if not request.user.is_staff:
            parameters['owner_id'] = request.user.id

        wallets = WalletRepository.get_all_wallets(**parameters)

        return wallets

    @staticmethod
    def wallet_details(wallet_id: int) -> Wallet:
        """
        Get the details of a wallet by accessing the repository.

        Args:
            wallet_id (int): The wallet id.

        Returns:
            Wallet: The wallet instance.
        """

        wallet = WalletRepository.get_single_wallet(wallet_id)

        return wallet

    @staticmethod
    def update_wallet(wallet_id: int, request_data: dict) -> Wallet:
        """
        Request to update a wallet by accessing the repository.

        Args:
            wallet_id (int): The wallet id.

        Returns:
            Wallet: The wallet instance.
        """

        co_owners = request_data.pop('co_owners', [])
        wallet = WalletRepository.get_single_wallet(wallet_id)

        for key, value in request_data.items():
            setattr(wallet, key, value)

        WalletRepository.save_wallet(wallet)

        if co_owners:
            WalletRepository.add_co_owners_to_wallet(wallet, co_owners)
        
        else:
            WalletRepository.erase_co_owners_from_wallet(wallet)

        return wallet

    @staticmethod
    def delete_wallet(wallet_id: int) -> None:
        """
        Request to delete a wallet by accessing the repository.

        Args:
            wallet_id (int): The wallet id.

        Returns:
            None
        """

        wallet = WalletRepository.get_single_wallet(wallet_id)

        WalletRepository.delete_wallet(wallet)

        return None
