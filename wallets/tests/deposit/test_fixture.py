import pytest

from django.utils import timezone

from wallets.models import Deposit

from wallets.tests.test_fixture import test_user, test_currencies, test_countries
from wallets.tests.wallet.test_fixture import test_wallets
from wallets.tests.account.test_fixture import test_accounts, test_account_types, test_account_institution_types, test_institution

@pytest.fixture
def test_deposits(test_accounts, test_currencies, test_wallets, test_user):
    deposits = []
    deposits_data = [
        {'wallet': test_wallets[0], 'account': test_accounts[0], 'user': test_user[0], 'amount': 100.00, 'currency': test_currencies[0], 'description': 'Deposit 1', 'deposited_at': timezone.now()},
        {'wallet': test_wallets[0], 'account': test_accounts[0], 'user': test_user[0], 'amount': 200.00, 'currency': test_currencies[0], 'description': 'Deposit 2', 'deposited_at': timezone.now()},
        {'wallet': test_wallets[0], 'account': test_accounts[0], 'user': test_user[0], 'amount': 300.00, 'currency': test_currencies[0], 'description': 'Deposit 3', 'deposited_at': timezone.now()},
        {'wallet': test_wallets[0], 'account': test_accounts[0], 'user': test_user[0], 'amount': 400.00, 'currency': test_currencies[0], 'description': 'Deposit 4', 'deposited_at': timezone.now()},
        {'wallet': test_wallets[0], 'account': test_accounts[0], 'user': test_user[0], 'amount': 500.00, 'currency': test_currencies[0], 'description': 'Deposit 5', 'deposited_at': timezone.now()}
    ]

    for deposit in deposits_data:
        deposits.append(Deposit.objects.create(wallet=deposit['wallet'], account=deposit['account'], user=deposit['user'], amount=deposit['amount'], currency=deposit['currency'], description=deposit['description'], deposited_at=deposit['deposited_at']))

    return deposits