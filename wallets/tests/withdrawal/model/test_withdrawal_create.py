import pytest

from django.utils import timezone
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from wallets.models import Withdrawal, Deposit
from wallets.tests.test_fixture import test_user, test_currencies, test_countries
from wallets.tests.wallet.test_fixture import test_wallets
from wallets.tests.account.test_fixture import test_accounts, test_institution, test_account_types, test_account_institution_types

@pytest.mark.django_db
def test_withdrawal_create(test_user, test_wallets, test_accounts, test_currencies):
    """
    Test the creation of a Withdrawal model instance.
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

    assert withdrawal.wallet == withdrawal_data['wallet']
    assert withdrawal.account == withdrawal_data['account']
    assert withdrawal.currency == withdrawal_data['currency']
    assert withdrawal.amount == withdrawal_data['amount']
    assert withdrawal.description == withdrawal_data['description']
    assert withdrawal.withdrawn_at == withdrawal_data['withdrawn_at']
    assert withdrawal.created_at
    assert withdrawal.updated_at


@pytest.mark.django_db
def test_withdrawal_create_no_user(test_wallets, test_accounts, test_currencies):

    withdrawal_data = {
        'wallet': test_wallets[0],
        'account': test_accounts[0],
        'currency': test_currencies[0],
        'amount': 100.00,
        'description': 'Test withdrawal',
        'withdrawn_at': timezone.now()
    }

    check_withdrawal_validations(withdrawal_data, 'user', 'Withdrawal has no user.')


@pytest.mark.django_db
def test_withdrawal_create_no_wallet(test_user, test_accounts, test_currencies):

    withdrawal_data = {
        'user': test_user[0],
        'account': test_accounts[0],
        'currency': test_currencies[0],
        'amount': 100.00,
        'description': 'Test withdrawal',
        'withdrawn_at': timezone.now()
    }

    check_withdrawal_validations(withdrawal_data, 'wallet', 'Withdrawal has no wallet.')


@pytest.mark.django_db
def test_withdrawal_create_no_account(test_user, test_wallets, test_currencies):

    withdrawal_data = {
        'user': test_user[0],
        'wallet': test_wallets[0],
        'currency': test_currencies[0],
        'amount': 100.00,
        'description': 'Test withdrawal',
        'withdrawn_at': timezone.now()
    }

    check_withdrawal_validations(withdrawal_data, 'account', 'Withdrawal has no account.')


@pytest.mark.django_db
def test_withdrawal_create_no_currency(test_user, test_wallets, test_accounts):

    withdrawal_data = {
        'user': test_user[0],
        'wallet': test_wallets[0],
        'account': test_accounts[0],
        'amount': 100.00,
        'description': 'Test withdrawal',
        'withdrawn_at': timezone.now()
    }

    check_withdrawal_validations(withdrawal_data, 'currency', 'Withdrawal has no currency.')


@pytest.mark.django_db
def test_withdrawal_create_with_currency_not_in_db(test_user, test_wallets, test_accounts):

    withdrawal_data = {
        'user': test_user[0],
        'wallet': test_wallets[0],
        'account': test_accounts[0],
        'currency': 'XXX',
        'amount': 100.00,
        'description': 'Test withdrawal',
        'withdrawn_at': timezone.now()
    }

    check_withdrawal_validations(withdrawal_data, 'currency', 'Cannot assign "\'XXX\'": "Withdrawal.currency" must be a "Currency" instance.')


@pytest.mark.django_db
def test_withdrawal_create_with_currency_not_in_account(test_user, test_wallets, test_accounts, test_currencies):

    withdrawal_data = {
        'user': test_user[0],
        'wallet': test_wallets[0],
        'account': test_accounts[0],
        'currency': test_currencies[1],
        'amount': 100.00,
        'description': 'Test withdrawal',
        'withdrawn_at': timezone.now()
    }

    check_withdrawal_validations(withdrawal_data, 'currency', 'The currency of the withdrawal must be the same as the currency of the account.')


@pytest.mark.django_db
def test_withdrawal_create_no_amount(test_user, test_wallets, test_accounts, test_currencies):

    withdrawal_data = {
        'user': test_user[0],
        'wallet': test_wallets[0],
        'account': test_accounts[0],
        'currency': test_currencies[0],
        'description': 'Test withdrawal',
        'withdrawn_at': timezone.now()
    }

    check_withdrawal_validations(withdrawal_data, 'amount', 'This field cannot be null.')


@pytest.mark.django_db
def test_withdrawal_create_negative_amount(test_user, test_wallets, test_accounts, test_currencies):
    
    withdrawal_data = {
        'user': test_user[0],
        'wallet': test_wallets[0],
        'account': test_accounts[0],
        'currency': test_currencies[0],
        'amount': -100.00,
        'description': 'Test withdrawal',
        'withdrawn_at': timezone.now()
    }

    check_withdrawal_validations(withdrawal_data, 'amount', 'Ensure this value is greater than or equal to 0.01.')


@pytest.mark.django_db
def test_withdrawal_create_amount_more_than_current_balance(test_user, test_wallets, test_accounts, test_currencies):
    
    withdrawal_data = {
        'user': test_user[0],
        'wallet': test_wallets[0],
        'account': test_accounts[0],
        'currency': test_currencies[0],
        'amount': 1000.00,
        'description': 'Test withdrawal',
        'withdrawn_at': timezone.now()
    }

    check_withdrawal_validations(withdrawal_data, 'amount', 'Insufficient funds to make this withdrawal.')

@pytest.mark.django_db
def test_withdrawal_create_amount_equal_zero(test_user, test_wallets, test_accounts, test_currencies):
    
    withdrawal_data = {
        'user': test_user[0],
        'wallet': test_wallets[0],
        'account': test_accounts[0],
        'currency': test_currencies[0],
        'amount': 0.00,
        'description': 'Test withdrawal',
        'withdrawn_at': timezone.now()
    }

    check_withdrawal_validations(withdrawal_data, 'amount', 'Ensure this value is greater than or equal to 0.01.')


@pytest.mark.django_db
def test_withdrawal_too_long_description(test_user, test_wallets, test_accounts, test_currencies):
    
        withdrawal_data = {
            'user': test_user[0],
            'wallet': test_wallets[0],
            'account': test_accounts[0],
            'currency': test_currencies[0],
            'amount': 100.00,
            'description': 'a' * 1001,
            'withdrawn_at': timezone.now()
        }
    
        check_withdrawal_validations(withdrawal_data, 'description', 'Ensure this value has at most 1000 characters (it has 1001).')


@pytest.mark.django_db
def test_withdrawal_no_withdrawn_at(test_user, test_wallets, test_accounts, test_currencies):

    withdrawal_data = {
        'user': test_user[0],
        'wallet': test_wallets[0],
        'account': test_accounts[0],
        'currency': test_currencies[0],
        'amount': 100.00,
        'description': 'Test withdrawal'
    }

    check_withdrawal_validations(withdrawal_data, 'withdrawn_at', 'This field cannot be null.')


@pytest.mark.django_db
def test_withdrawal_future_withdrawn_at(test_user, test_wallets, test_accounts, test_currencies):

    withdrawal_data = {
        'user': test_user[0],
        'wallet': test_wallets[0],
        'account': test_accounts[0],
        'currency': test_currencies[0],
        'amount': 100.00,
        'description': 'Test withdrawal',
        'withdrawn_at': timezone.now() + timezone.timedelta(days=1)
    }

    check_withdrawal_validations(withdrawal_data, 'withdrawn_at', 'Date cannot be in the future.')



def check_withdrawal_validations(withdrawl_data, error_field, error_message):


    with pytest.raises((ValidationError, ObjectDoesNotExist, ValueError)) as exception_info:
 
        Withdrawal.objects.create(**withdrawl_data)

    try:
        assert exception_info.value.message_dict[error_field][0] == error_message
        assert Withdrawal.objects.count() == 0

    except AttributeError:
        assert error_message in str(exception_info.value)
        assert Withdrawal.objects.count() == 0