import pytest

from django.utils import timezone

from wallets.models import Withdrawal

from wallets.tests.test_fixture import test_user, test_currencies, test_countries
from wallets.tests.wallet.test_fixture import test_wallets
from wallets.tests.account.test_fixture import test_accounts, test_account_types, test_account_institution_types, test_institution
from wallets.tests.deposit.test_fixture import test_deposits


@pytest.fixture
def test_withdrawals(test_accounts, test_currencies, test_wallets, test_user, test_deposits):
    withdrawals = []
    withdrawals_data = [
        {'wallet': test_wallets[0], 'account': test_accounts[0], 'user': test_user[0], 'amount': 100.00, 'currency': test_currencies[0], 'description': 'Withdrawal 1', 'withdrawn_at': timezone.now()},
        {'wallet': test_wallets[0], 'account': test_accounts[0], 'user': test_user[0], 'amount': 200.00, 'currency': test_currencies[0], 'description': 'Withdrawal 2', 'withdrawn_at': timezone.now()},
        {'wallet': test_wallets[0], 'account': test_accounts[0], 'user': test_user[0], 'amount': 300.00, 'currency': test_currencies[0], 'description': 'Withdrawal 3', 'withdrawn_at': timezone.now()},
        {'wallet': test_wallets[0], 'account': test_accounts[0], 'user': test_user[0], 'amount': 400.00, 'currency': test_currencies[0], 'description': 'Withdrawal 4', 'withdrawn_at': timezone.now()},
        {'wallet': test_wallets[0], 'account': test_accounts[0], 'user': test_user[0], 'amount': 500.00, 'currency': test_currencies[0], 'description': 'Withdrawal 5', 'withdrawn_at': timezone.now()}
    ]

    for withdrawal in withdrawals_data:
        withdrawals.append(Withdrawal.objects.create(wallet=withdrawal['wallet'], account=withdrawal['account'], user=withdrawal['user'], amount=withdrawal['amount'], currency=withdrawal['currency'], description=withdrawal['description'], withdrawn_at=withdrawal['withdrawn_at']))

    return withdrawals