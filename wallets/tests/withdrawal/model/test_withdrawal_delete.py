import pytest


from wallets.models import Withdrawal

from wallets.tests.test_fixture import test_user, test_currencies, test_countries
from wallets.tests.wallet.test_fixture import test_wallets
from wallets.tests.account.test_fixture import test_accounts, test_account_types, test_account_institution_types, test_institution
from wallets.tests.deposit.test_fixture import test_deposits
from wallets.tests.withdrawal.test_fixture import test_withdrawals

@pytest.mark.django_db
def test_delete_withdrawal(test_withdrawals):

    count_before = Withdrawal.objects.count()  

    withdrawal = test_withdrawals[0]
    withdrawal.delete()

    assert Withdrawal.objects.count() == count_before - 1
