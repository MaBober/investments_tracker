from wallets.models import Wallet
from wallets.repository import WalletRepository


class WalletController:

    @staticmethod
    def build_wallet(request_data: dict, owner):
        """
        Create a wallet instance from the request data.

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
    def list_wallets(**parameters):
        """
        List all wallets.

        Returns:
            QuerySet: The wallets.
        """

        wallets = WalletRepository.get_all_wallets(**parameters)

        return wallets

    @staticmethod
    def wallet_details(wallet_id: int):
        """
        Get the details of a wallet.

        Args:
            wallet_id (int): The wallet id.

        Returns:
            Wallet: The wallet instance.
        """

        wallet = WalletRepository.get_single_wallet(wallet_id)

        return wallet

    @staticmethod
    def update_wallet(wallet_id: int, request_data: dict):
        """
        Update the details of a wallet.

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
    def delete_wallet(wallet_id: int):
        """
        Delete a wallet.

        Args:
            wallet_id (int): The wallet id.
        """

        wallet = WalletRepository.get_single_wallet(wallet_id)

        WalletRepository.delete_wallet(wallet)
