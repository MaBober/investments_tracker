from datetime import datetime
from typing import List

from django.db.models import QuerySet, Q
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User

from wallets.models import Wallet


class WalletRepository:
    """
    Repository for the Wallet model.

    This repository contains the methods that should be used to perform actions on the Wallet model.
    """

    @staticmethod
    def create_wallet(request_data: dict, owner_id: int) -> Wallet:
        """
        Create a wallet instance from the request data.

        Args:
            request_data (dict): The request data.
            owner (int): The owner id.

        Returns:
            Wallet: The wallet instance.
        """

        wallet = Wallet.objects.create(owner_id=owner_id, **request_data)

        return wallet

    @staticmethod
    def add_co_owners_to_wallet(wallet: Wallet, co_owners: list) -> None:
        """
        Add co-owners to the wallet.

        Args:
            wallet (Wallet): The wallet instance.
            co_owners (list): The co-owners of the wallet.
        """

        wallet.co_owners.clear()
        wallet.co_owners.add(*co_owners)

    @staticmethod
    def erase_co_owners_from_wallet(wallet: Wallet) -> None:
        """
        Erase co-owners from the wallet.

        Args:
            wallet (Wallet): The wallet instance.
        """

        wallet.co_owners.clear()

    @staticmethod
    def get_all_wallets(
        owner_id: List[int],
        co_owner_id: List[int],
        created_before: datetime,
        created_after: datetime,
        user_id,
    ) -> QuerySet[Wallet]:
        """
        List all wallets.

        Args:
            owner_id (int): The owner id.
            created_before (datetime): The date before which the wallets were created.
            created_after (datetime): The date after which the wallets were created.
            user_id (int): The id of user sending  equest.

        Returns:
            QuerySet: The filltred wallets.
        """

        filters = {}

        if owner_id:
            filters["owner_id__in"] = owner_id
        if co_owner_id:
            filters["co_owners__in"] = co_owner_id
        if created_before:
            filters["created_at__lt"] = created_before
        if created_after:
            filters["created_at__gt"] = created_after

        all_wallets = Wallet.objects.filter(**filters)

        if user_id:
            all_wallets = all_wallets.filter(
                Q(owner_id=user_id) | Q(co_owners__in=[user_id])
            )

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

        try:
            wallet = Wallet.objects.get(id=wallet_id)
        except ObjectDoesNotExist:
            wallet = None

        return wallet

    @staticmethod
    def save_wallet(wallet: Wallet) -> None:
        """
        Save the wallet instance.

        Args:
            wallet (Wallet): The wallet instance.
        """

        wallet.save()

    @staticmethod
    def delete_wallet(wallet: Wallet) -> None:
        """
        Delete the wallet instance.

        Args:
            wallet (Wallet): The wallet instance.
        """

        wallet.delete()
