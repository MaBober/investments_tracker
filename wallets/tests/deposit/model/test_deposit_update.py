import pytest

from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Count


from wallets.models import Wallet, Account, Deposit

from wallets.tests.test_fixture import test_user, test_currencies, test_countries
from wallets.tests.wallet.test_fixture import test_wallets
from wallets.tests.account.test_fixture import test_accounts, test_account_types, test_account_institution_types, test_institution

@pytest.mark.django_db
def test_deposit_update(test_user, test_currencies, test_wallets, test_accounts, test_account_types, test_account_institution_types, test_institution):

    # Create a deposit
    deposit = Deposit.objects.create(
        wallet=test_wallets[0],
        account=test_accounts[0],
        user=test_user[0],
        amount=1000.00,
        currency=test_currencies[0],
        description='Initial deposit',
        deposited_at=timezone.now()
    )


    with pytest.raises(ValidationError) as exception_info:
        deposit.amount = 2000.00
        deposit.description = 'Updated deposit'
        deposit.save()

    assert exception_info.value.message_dict['update_deposit'][0] == 'Updating deposits will be added soon.'
