import pytest

from rest_framework.test import APIClient

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from wallets.models import Wallet


@pytest.fixture
def test_wallets(test_user):

    wallets = []
    wallets_data = [
        {'owner': test_user[0], 'name': 'John Wallet', 'description': 'John Wallet description'},
        {'owner': test_user[1], 'name': 'Paul Wallet', 'description': 'Paul Wallet description', 'co_owners': [test_user[2]]},
        {'owner': test_user[2], 'name': 'George Wallet', 'description': 'George Wallet description'},
        {'owner': test_user[3], 'name': 'Ringo Wallet', 'description': 'Ringo Wallet description'},
        {'owner': test_user[0], 'name': 'John Wallet 2', 'description': 'John Wallet 2 description'}
    ]

    for wallet in wallets_data:
        wallets.append(Wallet.objects.create(owner=wallet['owner'], name=wallet['name'], description=wallet['description']))
        if 'co_owners' in wallet:
            wallets[-1].co_owners.set(wallet['co_owners'])
    
    return wallets

