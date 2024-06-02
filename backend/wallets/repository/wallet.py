from django.db.models import QuerySet
from django.core.exceptions import FieldDoesNotExist

from django.contrib.auth.models import User

from wallets.models import Wallet

class WalletRepository:
    """
    Repository for the Wallet model.
    
    This repository contains the methods that should be used to perform actions on the Wallet model.

    Methods:
        create_wallet: A method that creates a wallet instance from the request data.
        add_co_owners_to_wallet: A method that adds co-owners to the wallet.
        erase_co_owners_from_wallet: A method that erases co-owners from the wallet.
        get_all_wallets: A method that lists all wallets.
        get_single_wallet: A method that gets the details of a wallet.
        save_wallet: A method that saves the wallet instance.
        delete_wallet: A method that deletes the wallet instance.
    """

    @staticmethod
    def create_wallet(request_data: dict, owner: User) -> Wallet:
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
    def add_co_owners_to_wallet(wallet: Wallet, co_owners: list) -> None:
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
    def erase_co_owners_from_wallet(wallet: Wallet) -> None:
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

        valid_parameters = {}
        for key in parameters:
            try:
                Wallet._meta.get_field(key)
                valid_parameters[key] = parameters[key]
            except FieldDoesNotExist:
                continue

        all_wallets = Wallet.objects.filter(**valid_parameters)

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
    def save_wallet(wallet: Wallet) -> None:
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
    def delete_wallet(wallet: Wallet) -> None:
        """
        Delete the wallet instance.

        Args:
            wallet (Wallet): The wallet instance.
        """
        try:
            wallet.delete()
        except Exception as e:
            raise e
            