import pytest

from django.utils import timezone
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from wallets.models import Withdrawal, Deposit, MarketAssetTransaction
from wallets.tests.test_fixture import test_user, test_currencies, test_countries
from wallets.tests.wallet.test_fixture import test_wallets
from wallets.tests.account.test_fixture import test_accounts, test_institution, test_account_types, test_account_institution_types
from wallets.tests.asset.test_fixture import test_asset_types, test_exchange_marketes, test_market_shares


@pytest.mark.django_db
def test_transaction_delete(test_user, test_wallets, test_accounts, test_currencies, test_market_shares):
    """
    Test the deletion of a Transaction model instance.
    """

    Deposit.objects.create(
        user=test_user[0],
        wallet=test_wallets[0],
        account=test_accounts[0],
        currency=test_currencies[0],
        amount=10220.00,
        description='Test deposit',
        deposited_at=timezone.now()
    )

    transaction_data = {
        'user': test_user[0],
        'transaction_type': 'B',
        'account': test_accounts[0],
        'wallet': test_wallets[0],
        'asset': test_market_shares[0],
        'amount': 100.00,
        'price': 1.00,
        'currency': test_currencies[0],
        'currency_price': 1.00,
        'commission': 0.00,
        'commission_currency': test_currencies[0],
        'commission_currency_price': 1.00,
        'transaction_date': timezone.now()
    }

    transaction = MarketAssetTransaction.objects.create(**transaction_data)

    assert MarketAssetTransaction.objects.count() == 1

    transaction = MarketAssetTransaction.objects.first()

    with pytest.raises(ValidationError) as exception_info:

        transaction.delete()

    assert exception_info.value.message_dict['transaction_delete_unavailable'][0] == 'Deleting a transaction will be added soon.'
    assert MarketAssetTransaction.objects.count() == 1