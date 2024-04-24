import pytest

from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils import timezone
from django.db.models import Count


from wallets.models import Wallet, Account, Deposit

from wallets.tests.test_fixture import test_user, test_currencies, test_countries
from wallets.tests.wallet.test_fixture import test_wallets
from wallets.tests.account.test_fixture import test_accounts, test_account_types, test_account_institution_types, test_institution

@pytest.mark.django_db
def test_deposit_create(test_user, test_wallets, test_accounts, test_currencies):

    current_time = timezone.now()
    # Create a deposit for the account
    Deposit.objects.create(
        wallet=test_wallets[0],
        account=test_accounts[0],
        user=test_user[0],
        amount=100.00,
        currency=test_currencies[0],
        description='This is a test deposit',
        deposited_at=current_time - timezone.timedelta(days=1)
    )

    # Check that a Deposit object has been added to the database
    assert Deposit.objects.count() == 1

    # Retrieve the deposit from the database
    deposit = Deposit.objects.first()

    # Check the attributes of the deposit
    assert deposit.wallet == test_wallets[0]
    assert deposit.account == test_accounts[0]
    assert deposit.user == test_user[0]
    assert deposit.amount == 100.00
    assert deposit.currency == test_currencies[0]
    assert deposit.description == 'This is a test deposit'
    assert deposit.deposited_at is not None
    assert deposit.created_at is not None
    assert deposit.updated_at is not None
    assert deposit.created_at == deposit.updated_at
    assert timezone.now() - deposit.created_at < timezone.timedelta(seconds=1.5)
    assert deposit.deposited_at == current_time - timezone.timedelta(days=1)

@pytest.mark.django_db
def test_deposit_create_no_wallet(test_user, test_accounts, test_currencies):
    
    check_deposit_validations(
        wallet=None,
        account=test_accounts[0],
        user=test_user[0],
        amount=100.00,
        currency=test_currencies[0],
        description='This is a test deposit',
        deposited_at=timezone.now() - timezone.timedelta(days=1),
        error_field='wallet',
        error_message='Deposit has no wallet.'
    )

@pytest.mark.django_db
def test_deposit_create_no_account(test_user, test_wallets, test_currencies):
    
    check_deposit_validations(
        wallet=test_wallets[0],
        account=None,
        user=test_user[0],
        amount=100.00,
        currency=test_currencies[0],
        description='This is a test deposit',
        deposited_at=timezone.now() - timezone.timedelta(days=1),
        error_field='account',
        error_message='Deposit has no account.'
    )

@pytest.mark.django_db
def test_deposit_create_no_user(test_accounts, test_wallets, test_currencies):
    
    check_deposit_validations(
        wallet=test_wallets[0],
        account=test_accounts[0],
        user=None,
        amount=100.00,
        currency=test_currencies[0],
        description='This is a test deposit',
        deposited_at=timezone.now() - timezone.timedelta(days=1),
        error_field='user',
        error_message='Deposit has no user.'
    )

@pytest.mark.django_db
def test_deposit_create_no_amount(test_user, test_wallets, test_accounts, test_currencies):
    
    check_deposit_validations(
        wallet=test_wallets[0],
        account=test_accounts[0],
        user=test_user[0],
        amount=None,
        currency=test_currencies[0],
        description='This is a test deposit',
        deposited_at=timezone.now() - timezone.timedelta(days=1),
        error_field='amount',
        error_message='This field cannot be null.'
    )

@pytest.mark.django_db
def test_deposit_create_no_currency(test_user, test_wallets, test_accounts):
    
    check_deposit_validations(
        wallet=test_wallets[0],
        account=test_accounts[0],
        user=test_user[0],
        amount=100.00,
        currency=None,
        description='This is a test deposit',
        deposited_at=timezone.now() - timezone.timedelta(days=1),
        error_field='currency',
        error_message='This field cannot be null.'
    )

@pytest.mark.django_db
def test_deposit_create_too_long_description(test_user, test_wallets, test_accounts, test_currencies):

    check_deposit_validations(
        wallet=test_wallets[0],
        account=test_accounts[0],
        user=test_user[0],
        amount=100.00,
        currency=test_currencies[0],
        description='a' * 1001,
        deposited_at=timezone.now() - timezone.timedelta(days=1),
        error_field='description',
        error_message='Ensure this value has at most 1000 characters (it has 1001).'
    )

@pytest.mark.django_db
def test_deposit_create_no_deposited_at(test_user, test_wallets, test_accounts, test_currencies):
    
    check_deposit_validations(
        wallet=test_wallets[0],
        account=test_accounts[0],
        user=test_user[0],
        amount=100.00,
        currency=test_currencies[0],
        description='This is a test deposit',
        deposited_at=None,
        error_field='deposited_at',
        error_message='This field cannot be null.'
    )

@pytest.mark.django_db
def test_deposit_create_future_deposited_at(test_user, test_wallets, test_accounts, test_currencies):
    
    check_deposit_validations(
        wallet=test_wallets[0],
        account=test_accounts[0],
        user=test_user[0],
        amount=100.00,
        currency=test_currencies[0],
        description='This is a test deposit',
        deposited_at=timezone.now() + timezone.timedelta(days=1),
        error_field='deposited_at',
        error_message='Date cannot be in the future.'
    )

@pytest.mark.django_db
def test_deposit_create_negative_amount(test_user, test_wallets, test_accounts, test_currencies):
    
    check_deposit_validations(
        wallet=test_wallets[0],
        account=test_accounts[0],
        user=test_user[0],
        amount=-100.00,
        currency=test_currencies[0],
        description='This is a test deposit',
        deposited_at=timezone.now() - timezone.timedelta(days=1),
        error_field='amount',
        error_message='Ensure this value is greater than or equal to 0.01.'
    )

@pytest.mark.django_db
def test_deposit_create_zero_amount(test_user, test_wallets, test_accounts, test_currencies):
    
    check_deposit_validations(
        wallet=test_wallets[0],
        account=test_accounts[0],
        user=test_user[0],
        amount=0,
        currency=test_currencies[0],
        description='This is a test deposit',
        deposited_at=timezone.now() - timezone.timedelta(days=1),
        error_field='amount',
        error_message='Ensure this value is greater than or equal to 0.01.'
    )

#TODO: Write down all possibilities of errors regarding wallet and account ownership
@pytest.mark.django_db
def test_deposit_create_on_account_not_in_wallet(test_user, test_wallets, test_accounts, test_currencies):
        
        check_deposit_validations(
            wallet=test_wallets[0],
            account=test_accounts[1],
            user=test_user[0],
            amount=100.00,
            currency=test_currencies[0],
            description='This is a test deposit',
            deposited_at=timezone.now() - timezone.timedelta(days=1),
            error_field='account',
            error_message='Account does not belong to the wallet.'
        )

# @pytest.mark.django_db
# def test_deposit_create_on_wallet_not_owned_by_user(test_user, test_wallets, test_accounts, test_currencies):
        
#         check_deposit_validations(
#             wallet=test_wallets[2],
#             account=test_accounts[0],
#             user=test_user[0],
#             amount=100.00,
#             currency=test_currencies[0],
#             description='This is a test deposit',
#             deposited_at=timezone.now() - timezone.timedelta(days=1),
#             error_field='wallet',
#             error_message='Wallet does not belong to the user.'
#         )

# @pytest.mark.django_db
# def test_deposit_create_on_account_not_owned_by_user(test_user, test_wallets, test_accounts, test_currencies):
        
#         check_deposit_validations(
#             wallet=test_wallets[0],
#             account=test_accounts[3],
#             user=test_user[0],
#             amount=100.00,
#             currency=test_currencies[0],
#             description='This is a test deposit',
#             deposited_at=timezone.now() - timezone.timedelta(days=1),
#             error_field='account',
#             error_message='Account does not belong to the user.'
#         )

# @pytest.mark.django_db
# def test_deposit_on_wallet_co_owner(test_user, test_wallets, test_accounts, test_currencies):

#     wallets_with_co_owners = Wallet.objects.annotate(num_co_owners=Count('co_owners')).filter(num_co_owners__gt=0)
#     co_owner = wallets_with_co_owners[0].co_owners.first()


#     Deposit.objects.create(
#         wallet=wallets_with_co_owners[0],
#         account=test_accounts[1],
#         user=co_owner,
#         amount=100.00,
#         currency=test_currencies[0],
#         description='This is a test deposit',
#         deposited_at=timezone.now() - timezone.timedelta(days=1)
#     )

#     assert Deposit.objects.count() == 1

#     deposit = Deposit.objects.first()

#     assert deposit.wallet == wallets_with_co_owners[0]
#     assert deposit.account == test_accounts[1]
#     assert deposit.user == co_owner
#     assert deposit.amount == 100.00
#     assert deposit.currency == test_currencies[0]

# @pytest.mark.django_db
# def test_deposit_on_account_co_owner(test_user, test_wallets, test_accounts, test_currencies):

#     accounts_with_co_owners = Account.objects.annotate(num_co_owners=Count('co_owners')).filter(num_co_owners__gt=0)
#     co_owner = accounts_with_co_owners[0].co_owners.first()

#     Deposit.objects.create(
#         wallet=test_wallets[0],
#         account=accounts_with_co_owners[0],
#         user=co_owner,
#         amount=100.00,
#         currency=test_currencies[0],
#         description='This is a test deposit',
#         deposited_at=timezone.now() - timezone.timedelta(days=1)
#     )

#     assert Deposit.objects.count() == 1

#     deposit = Deposit.objects.first()

#     assert deposit.wallet == test_wallets[0]
#     assert deposit.account == accounts_with_co_owners[0]
#     assert deposit.user == co_owner
#     assert deposit.amount == 100.00
#     assert deposit.currency == test_currencies[0]

@pytest.mark.django_db
def test_deposit_with_currency_not_in_account(test_user, test_wallets, test_accounts, test_currencies):

    check_deposit_validations(
        wallet=test_wallets[0],
        account=test_accounts[0],
        user=test_user[0],
        amount=100.00,
        currency=test_currencies[1],
        description='This is a test deposit',
        deposited_at=timezone.now() - timezone.timedelta(days=1),
        error_field='__all__',
        error_message='The currency of the deposit must be the same as the currency of the account.'
    )


def check_deposit_validations(wallet, account, user, amount, currency, description, deposited_at, error_field, error_message):

    with pytest.raises((ValidationError, ObjectDoesNotExist)) as exception_info:
        Deposit.objects.create(
            wallet=wallet,
            account=account,
            user=user,
            amount=amount,
            currency=currency,
            description=description,
            deposited_at=deposited_at 
        )

    try:
        assert exception_info.value.message_dict[error_field][0] == error_message
        assert Deposit.objects.count() == 0

    except AttributeError:
        assert error_message in str(exception_info.value)
        assert Deposit.objects.count() == 0

