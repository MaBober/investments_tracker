import pytest

from django.utils import timezone
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from wallets.models import Transaction, TreasuryBondsTransaction, MarketAssetTransaction
from wallets.models import Account, Wallet, Currency, Deposit

from wallets.tests.test_fixture import test_user, test_currencies, test_countries
from wallets.tests.wallet.test_fixture import test_wallets
from wallets.tests.account.test_fixture import test_accounts, test_institution, test_account_types, test_account_institution_types
from wallets.tests.asset.test_fixture import test_asset_types, test_exchange_marketes, test_market_shares

@pytest.mark.django_db
def test_market_asset_transaction_create_buy(test_user, test_wallets, test_accounts, test_currencies, test_market_shares):
    """
    Test the creation of a MarketAssetTransaction model instance.
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

    assert transaction.user == transaction_data['user']
    assert transaction.transaction_type == transaction_data['transaction_type']
    assert transaction.account == transaction_data['account']
    assert transaction.wallet == transaction_data['wallet']
    assert transaction.amount == transaction_data['amount']
    assert transaction.price == transaction_data['price']
    assert transaction.currency == transaction_data['currency']
    assert transaction.currency_price == transaction_data['currency_price']
    assert transaction.commission == transaction_data['commission']
    assert transaction.commission_currency == transaction_data['commission_currency']
    assert transaction.commission_currency_price == transaction_data['commission_currency_price']
    assert transaction.transaction_date == transaction_data['transaction_date']
    assert transaction.created_at
    assert transaction.updated_at

    user_to_check = test_user[0]

    assert test_accounts[0].get_balance(test_currencies[0]) == 0.00
    assert user_to_check.assets.all().count() == 1
    assert user_to_check.assets.all().first().amount == transaction_data['amount']
    assert user_to_check.assets.all().first().price == transaction_data['price']
    assert user_to_check.assets.all().first().currency == transaction_data['currency']
    assert user_to_check.assets.all().first().currency_price == transaction_data['currency_price']
    assert user_to_check.assets.all().first().commission == transaction_data['commission']
    assert user_to_check.assets.all().first().commission_currency == transaction_data['commission_currency']
    assert user_to_check.assets.all().first().commission_currency_price == transaction_data['commission_currency_price']
    assert user_to_check.assets.all().first().active == True
    assert user_to_check.assets.all().first().buy_transaction == transaction


@pytest.mark.django_db
def test_market_asset_transaction_create_sell(test_user, test_wallets, test_accounts, test_currencies, test_market_shares):
    """
    Test the creation of a MarketAssetTransaction model instance.
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

    but_transaction = MarketAssetTransaction.objects.create(
        user=test_user[0],
        transaction_type='B',
        account=test_accounts[0],
        wallet=test_wallets[0],
        asset=test_market_shares[0],
        amount=100.00,
        price=1.00,
        currency=test_currencies[0],
        currency_price=1.00,
        commission=0.00,
        commission_currency=test_currencies[0],
        commission_currency_price=1.00,
        transaction_date=timezone.now()
    )

    transaction_data = {
        'user': test_user[0],
        'transaction_type': 'S',
        'account': test_accounts[0],
        'wallet': test_wallets[0],
        'asset': test_market_shares[0],
        'amount': 100.00,
        'price': 2.00,
        'currency': test_currencies[0],
        'currency_price': 1.00,
        'commission': 0.00,
        'commission_currency': test_currencies[0],
        'commission_currency_price': 1.00,
        'transaction_date': timezone.now()
    }

    transaction = MarketAssetTransaction.objects.create(**transaction_data)

    assert MarketAssetTransaction.objects.count() == 2

    transaction = MarketAssetTransaction.objects.last()

    assert transaction.user == transaction_data['user']
    assert transaction.transaction_type == transaction_data['transaction_type']
    assert transaction.account == transaction_data['account']
    assert transaction.wallet == transaction_data['wallet']
    assert transaction.amount == transaction_data['amount']
    assert transaction.price == transaction_data['price']
    assert transaction.currency == transaction_data['currency']
    assert transaction.currency_price == transaction_data['currency_price']
    assert transaction.commission == transaction_data['commission']
    assert transaction.commission_currency == transaction_data['commission_currency']
    assert transaction.commission_currency_price == transaction_data['commission_currency_price']
    assert transaction.transaction_date

    user_to_check = test_user[0]

    assert test_accounts[0].get_balance(test_currencies[0]) == transaction_data['amount'] * transaction_data['price']
    assert user_to_check.assets.all().count() == 1
    assert user_to_check.assets.all().first().amount == 0.00
    assert user_to_check.assets.all().first().price == but_transaction.price
    assert user_to_check.assets.all().first().currency == but_transaction.currency
    assert user_to_check.assets.all().first().currency_price == but_transaction.currency_price
    assert user_to_check.assets.all().first().commission == but_transaction.commission
    assert user_to_check.assets.all().first().commission_currency == but_transaction.commission_currency
    assert user_to_check.assets.all().first().commission_currency_price == but_transaction.commission_currency_price
    assert user_to_check.assets.all().first().active == False
    assert list(user_to_check.assets.all().first().sell_transactions.all()) == [transaction]


@pytest.mark.django_db
def test_market_asset_transaction_create_no_user(test_wallets, test_accounts, test_currencies, test_market_shares):
    """
    Test the validations of a MarketAssetTransaction model instance.
    """

    transaction_data = {
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

    check_market_asset_transaction_validations(transaction_data, 'user', 'This field cannot be null.')


@pytest.mark.django_db
def test_market_asset_transaction_create_no_transaction_type(test_user, test_wallets, test_accounts, test_currencies, test_market_shares):
    """
    Test the validations of a MarketAssetTransaction model instance.
    """

    transaction_data = {
        'user': test_user[0],
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

    check_market_asset_transaction_validations(transaction_data, 'transaction_type', 'This field cannot be blank.')


@pytest.mark.django_db
def test_market_asset_transaction_create_transaction_type_invalid(test_user, test_wallets, test_accounts, test_currencies, test_market_shares):
    """
    Test the validations of a MarketAssetTransaction model instance.
    """

    transaction_data = {
        'user': test_user[0],
        'transaction_type': 'X',
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

    check_market_asset_transaction_validations(transaction_data, 'transaction_type', 'Value \'X\' is not a valid choice.')


@pytest.mark.django_db
def test_market_asset_transaction_create_no_account(test_user, test_wallets, test_currencies, test_market_shares):
    """
    Test the validations of a MarketAssetTransaction model instance.
    """

    transaction_data = {
        'user': test_user[0],
        'transaction_type': 'B',
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

    check_market_asset_transaction_validations(transaction_data, 'account', 'This field cannot be null.')


@pytest.mark.django_db
def test_market_asset_transaction_create_no_wallet(test_user, test_accounts, test_currencies, test_market_shares):
    """
    Test the validations of a MarketAssetTransaction model instance.
    """

    transaction_data = {
        'user': test_user[0],
        'transaction_type': 'B',
        'account': test_accounts[0],
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

    check_market_asset_transaction_validations(transaction_data, 'wallet', 'This field cannot be null.')


@pytest.mark.django_db
def test_market_asset_transaction_create_no_asset(test_user, test_wallets, test_accounts, test_currencies):
    """
    Test the validations of a MarketAssetTransaction model instance.
    """

    transaction_data = {
        'user': test_user[0],
        'transaction_type': 'B',
        'account': test_accounts[0],
        'wallet': test_wallets[0],
        'amount': 100.00,
        'price': 1.00,
        'currency': test_currencies[0],
        'currency_price': 1.00,
        'commission': 0.00,
        'commission_currency': test_currencies[0],
        'commission_currency_price': 1.00,
        'transaction_date': timezone.now()
    }

    check_market_asset_transaction_validations(transaction_data, 'asset', 'This field cannot be null.')


@pytest.mark.django_db
def test_market_asset_transaction_create_no_amount(test_user, test_wallets, test_accounts, test_currencies, test_market_shares):
    """
    Test the validations of a MarketAssetTransaction model instance.
    """

    transaction_data = {
        'user': test_user[0],
        'transaction_type': 'B',
        'account': test_accounts[0],
        'wallet': test_wallets[0],
        'asset': test_market_shares[0],
        'price': 1.00,
        'currency': test_currencies[0],
        'currency_price': 1.00,
        'commission': 0.00,
        'commission_currency': test_currencies[0],
        'commission_currency_price': 1.00,
        'transaction_date': timezone.now()
    }

    check_market_asset_transaction_validations(transaction_data, 'amount', 'This field cannot be null.')

@pytest.mark.django_db
def test_market_asset_transaction_create_amount_negative(test_user, test_wallets, test_accounts, test_currencies, test_market_shares):
    """
    Test the validations of a MarketAssetTransaction model instance.
    """

    transaction_data = {
        'user': test_user[0],
        'transaction_type': 'B',
        'account': test_accounts[0],
        'wallet': test_wallets[0],
        'asset': test_market_shares[0],
        'amount': -100.00,
        'price': 1.00,
        'currency': test_currencies[0],
        'currency_price': 1.00,
        'commission': 0.00,
        'commission_currency': test_currencies[0],
        'commission_currency_price': 1.00,
        'transaction_date': timezone.now()
    }

    check_market_asset_transaction_validations(transaction_data, 'amount', 'Ensure this value is greater than or equal to 0.')


@pytest.mark.django_db
def test_market_asset_transaction_create_amount_string(test_user, test_wallets, test_accounts, test_currencies, test_market_shares):
    """
    Test the validations of a MarketAssetTransaction model instance.
    """

    transaction_data = {
        'user': test_user[0],
        'transaction_type': 'B',
        'account': test_accounts[0],
        'wallet': test_wallets[0],
        'asset': test_market_shares[0],
        'amount': '10a0.00',
        'price': 1.00,
        'currency': test_currencies[0],
        'currency_price': 1.00,
        'commission': 0.00,
        'commission_currency': test_currencies[0],
        'commission_currency_price': 1.00,
        'transaction_date': timezone.now()
    }

    check_market_asset_transaction_validations(transaction_data, 'amount', '“10a0.00” value must be a decimal number.')


@pytest.mark.django_db
def test_market_asset_transaction_create_no_price(test_user, test_wallets, test_accounts, test_currencies, test_market_shares):
    """
    Test the validations of a MarketAssetTransaction model instance.
    """

    transaction_data = {
        'user': test_user[0],
        'transaction_type': 'B',
        'account': test_accounts[0],
        'wallet': test_wallets[0],
        'asset': test_market_shares[0],
        'amount': 100.00,
        'currency': test_currencies[0],
        'currency_price': 1.00,
        'commission': 0.00,
        'commission_currency': test_currencies[0],
        'commission_currency_price': 1.00,
        'transaction_date': timezone.now()
    }

    check_market_asset_transaction_validations(transaction_data, 'price', 'This field cannot be null.')


@pytest.mark.django_db
def test_market_asset_transaction_create_price_negative(test_user, test_wallets, test_accounts, test_currencies, test_market_shares):
    """
    Test the validations of a MarketAssetTransaction model instance.
    """

    transaction_data = {
        'user': test_user[0],
        'transaction_type': 'B',
        'account': test_accounts[0],
        'wallet': test_wallets[0],
        'asset': test_market_shares[0],
        'amount': 100.00,
        'price': -1.00,
        'currency': test_currencies[0],
        'currency_price': 1.00,
        'commission': 0.00,
        'commission_currency': test_currencies[0],
        'commission_currency_price': 1.00,
        'transaction_date': timezone.now()
    }

    check_market_asset_transaction_validations(transaction_data, 'price', 'Ensure this value is greater than or equal to 0.')


@pytest.mark.django_db
def test_market_asset_transaction_create_price_string(test_user, test_wallets, test_accounts, test_currencies, test_market_shares):
    """
    Test the validations of a MarketAssetTransaction model instance.
    """

    transaction_data = {
        'user': test_user[0],
        'transaction_type': 'B',
        'account': test_accounts[0],
        'wallet': test_wallets[0],
        'asset': test_market_shares[0],
        'amount': 100.00,
        'price': '10a0.00',
        'currency': test_currencies[0],
        'currency_price': 1.00,
        'commission': 0.00,
        'commission_currency': test_currencies[0],
        'commission_currency_price': 1.00,
        'transaction_date': timezone.now()
    }

    check_market_asset_transaction_validations(transaction_data, 'price', '“10a0.00” value must be a decimal number.')

@pytest.mark.django_db
def test_market_asset_transaction_create_no_currency(test_user, test_wallets, test_accounts, test_market_shares, test_currencies):
    """
    Test the validations of a MarketAssetTransaction model instance.
    """

    transaction_data = {
        'user': test_user[0],
        'transaction_type': 'B',
        'account': test_accounts[0],
        'wallet': test_wallets[0],
        'asset': test_market_shares[0],
        'amount': 100.00,
        'price': 1.00,
        'currency_price': 1.00,
        'commission': 0.00,
        'commission_currency': test_currencies[0],
        'commission_currency_price': 1.00,
        'transaction_date': timezone.now()
    }

    check_market_asset_transaction_validations(transaction_data, 'currency', 'This field cannot be null.')


@pytest.mark.django_db
def test_market_asset_transaction_create_currency_price_negative(test_user, test_wallets, test_accounts, test_currencies, test_market_shares):
    """
    Test the validations of a MarketAssetTransaction model instance.
    """

    transaction_data = {
        'user': test_user[0],
        'transaction_type': 'B',
        'account': test_accounts[0],
        'wallet': test_wallets[0],
        'asset': test_market_shares[0],
        'amount': 100.00,
        'price': 1.00,
        'currency': test_currencies[0],
        'currency_price': -1.00,
        'commission': 0.00,
        'commission_currency': test_currencies[0],
        'commission_currency_price': 1.00,
        'transaction_date': timezone.now()
    }

    check_market_asset_transaction_validations(transaction_data, 'currency_price', 'Ensure this value is greater than or equal to 0.')


@pytest.mark.django_db
def test_market_asset_transaction_create_currency_price_string(test_user, test_wallets, test_accounts, test_currencies, test_market_shares):
    """
    Test the validations of a MarketAssetTransaction model instance.
    """

    transaction_data = {
        'user': test_user[0],
        'transaction_type': 'B',
        'account': test_accounts[0],
        'wallet': test_wallets[0],
        'asset': test_market_shares[0],
        'amount': 100.00,
        'price': 1.00,
        'currency': test_currencies[0],
        'currency_price': '10a0.00',
        'commission': 0.00,
        'commission_currency': test_currencies[0],
        'commission_currency_price': 1.00,
        'transaction_date': timezone.now()
    }

    check_market_asset_transaction_validations(transaction_data, 'currency_price', '“10a0.00” value must be a decimal number.')


@pytest.mark.django_db
def test_market_asset_transaction_create_no_commission_currency(test_user, test_wallets, test_accounts, test_currencies, test_market_shares):
    """
    Test the validations of a MarketAssetTransaction model instance.
    """

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
        'commission_currency_price': 1.00,
        'transaction_date': timezone.now()
    }

    check_market_asset_transaction_validations(transaction_data, 'commission_currency', 'This field cannot be null.')


@pytest.mark.django_db
def test_market_asset_transaction_create_commission_currency_price_negative(test_user, test_wallets, test_accounts, test_currencies, test_market_shares):
    """
    Test the validations of a MarketAssetTransaction model instance.
    """

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
        'commission_currency_price': -1.00,
        'transaction_date': timezone.now()
    }

    check_market_asset_transaction_validations(transaction_data, 'commission_currency_price', 'Ensure this value is greater than or equal to 0.')


@pytest.mark.django_db
def test_market_asset_transaction_create_commission_currency_price_string(test_user, test_wallets, test_accounts, test_currencies, test_market_shares):
    """
    Test the validations of a MarketAssetTransaction model instance.
    """

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
        'commission_currency_price': '10a0.00',
        'transaction_date': timezone.now()
    }

    check_market_asset_transaction_validations(transaction_data, 'commission_currency_price', '“10a0.00” value must be a decimal number.')


@pytest.mark.django_db
def test_market_asset_transaction_create_no_transaction_date(test_user, test_wallets, test_accounts, test_currencies, test_market_shares):
    """
    Test the validations of a MarketAssetTransaction model instance.
    """

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
    }

    check_market_asset_transaction_validations(transaction_data, 'transaction_date', 'This field cannot be null.')

@pytest.mark.django_db
def test_market_asset_transaction_create_no_enough_balance(test_user, test_wallets, test_accounts, test_currencies, test_market_shares):

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

    check_market_asset_transaction_validations(transaction_data, 'not_enough_funds', 'The account does not have enough balance to make this transaction.')

@pytest.mark.django_db
def test_market_asset_transaction_create_sell_no_asset_owned(test_user, test_wallets, test_accounts, test_currencies, test_market_shares):
    """
    Test the validations of a MarketAssetTransaction model instance.
    """

    transaction_data = {
        'user': test_user[0],
        'transaction_type': 'S',
        'account': test_accounts[0],
        'wallet': test_wallets[0],
        'asset': test_market_shares[0],
        'amount': 100.00,
        'price': 2.00,
        'currency': test_currencies[0],
        'currency_price': 1.00,
        'commission': 0.00,
        'commission_currency': test_currencies[0],
        'commission_currency_price': 1.00,
        'transaction_date': timezone.now()
    }

    check_market_asset_transaction_validations(transaction_data, 'asset', 'You do not have enough assets to sell.')

def check_market_asset_transaction_validations(transaction_data, error_field, error_message, deposit_data=None, previous_transaction=None):
    """
    Check the validations of a MarketAssetTransaction model instance.
    """

    print(transaction_data)
    with pytest.raises((ValidationError, ObjectDoesNotExist, ValueError)) as exception_info:
        MarketAssetTransaction.objects.create(**transaction_data)

    try:
        assert exception_info.value.message_dict[error_field][0] == error_message
        assert MarketAssetTransaction.objects.count() == 0

    except AttributeError:
        assert error_message in str(exception_info.value)
        assert MarketAssetTransaction.objects.count() == 0