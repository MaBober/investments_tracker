from django.db.models import QuerySet

from wallets.models import Wallet

class WalletRepository:

    @staticmethod
    def create_wallet(request_data, owner):
        """
        Create a wallet instance from the request data.

        Args:
            request_data (dict): The request data.
            owner (User): The owner of the wallet.

        Returns:
            Wallet: The wallet instance.
        """
        try:
            wallet = Wallet.objects.create(owner=owner, **request_data)            

        except Exception as e:
            raise e
        
        return wallet

    @staticmethod
    def add_co_owners_to_wallet(wallet, co_owners):
        """
        Add co-owners to the wallet.

        Args:
            wallet (Wallet): The wallet instance.
            co_owners (list): The co-owners of the wallet.
        """
        try:
            wallet.co_owners.clear()
            wallet.co_owners.add(*co_owners)

        except Exception as e:
            raise e
        
    @staticmethod
    def erase_co_owners_from_wallet(wallet):
        """
        Erase co-owners from the wallet.

        Args:
            wallet (Wallet): The wallet instance.
        """
        try:
            wallet.co_owners.clear()

        except Exception as e:
            raise e
        
    @staticmethod
    def get_all_wallets(**parameters) -> QuerySet[Wallet]:
        """
        List all wallets.

        Returns:
            QuerySet: The wallets.
        """

        all_wallets = Wallet.objects.filter(**parameters)

        return all_wallets

    @staticmethod
    def get_single_wallet(wallet_id: int) -> Wallet:
        """
        Get the details of a wallet.

        Args:
            wallet_id (int): The wallet id.

        Returns:
            Wallet: The wallet instance.
        """

        wallet = Wallet.objects.get(id=wallet_id)

        return wallet

    @staticmethod
    def save_wallet(wallet):
        """
        Save the wallet instance.

        Args:
            wallet (Wallet): The wallet instance.
        """
        try:
            wallet.save()
        except Exception as e:
            raise e

    @staticmethod
    def delete_wallet(wallet):
        """
        Delete the wallet instance.

        Args:
            wallet (Wallet): The wallet instance.
        """
        try:
            wallet.delete()
        except Exception as e:
            raise e
            