import pytest

from django.utils import timezone
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from wallets.models import Withdrawal, Deposit
from wallets.tests.test_fixture import test_user, test_currencies, test_countries
from wallets.tests.wallet.test_fixture import test_wallets
from wallets.tests.account.test_fixture import test_accounts, test_institution, test_account_types, test_account_institution_types

@pytest.mark.django_db
def test_depostit_update(test_user, test_wallets, test_accounts, test_currencies):
    """
    Test the update of a Withdrawal model instance.
    """

    Deposit.objects.create(
        user=test_user[0],
        wallet=test_wallets[0],
        account=test_accounts[0],
        currency=test_currencies[0],
        amount=100.00,
        description='Test deposit',
        deposited_at=timezone.now()
    )

    withdrawal_data = {
        'user' : test_user[0],
        'wallet': test_wallets[0],
        'account': test_accounts[0],
        'currency': test_currencies[0],
        'amount': 100.00,
        'description': 'Test withdrawal',
        'withdrawn_at': timezone.now()
    }

    withdrawal = Withdrawal.objects.create(**withdrawal_data)

    assert Withdrawal.objects.count() == 1

    withdrawal = Withdrawal.objects.first()

    with pytest.raises(ValidationError) as exception_info:

        withdrawal.amount = 20.00
        withdrawal.description = 'Updated description'

        withdrawal.save()

    assert exception_info.value.message_dict['update_sell_transaction'][0] == 'Updating sell transaction will be added soon.'


