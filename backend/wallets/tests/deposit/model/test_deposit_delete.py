import pytest


from wallets.models import Deposit

from wallets.tests.test_fixture import test_user, test_currencies, test_countries
from wallets.tests.wallet.test_fixture import test_wallets
from wallets.tests.account.test_fixture import test_accounts, test_account_types, test_account_institution_types, test_institution
from wallets.tests.deposit.test_fixture import test_deposits

@pytest.mark.django_db
def test_delete_deposit(test_deposits):

    count_before = Deposit.objects.count()  

    deposit = test_deposits[0]
    deposit.delete()

    assert Deposit.objects.count() == count_before - 1
