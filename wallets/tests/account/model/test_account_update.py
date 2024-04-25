import pytest

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from wallets.models import Wallet, Account, AccountType, AccountInstitution, AccountInstitutionType
from wallets.tests.test_fixture import test_countries, test_currencies, test_user
from wallets.tests.account.test_fixture import test_account_types, test_account_institution_types, test_institution, test_accounts
from wallets.tests.wallet.test_fixture import test_wallets

@pytest.mark.django_db
def test_account_udpate(test_user, test_account_types, test_account_institution_types, test_institution, test_wallets, test_accounts, test_currencies):

    
    for i in range(0, 2):

        account_to_update = test_accounts[i]
        
        # Update the account
        account_to_update.name = 'Updated Account Name' + str([i])
        account_to_update.description = 'Updated Account Description'
        account_to_update.type = test_account_types[1]
        account_to_update.institution = test_institution[1]
        account_to_update.currencies.set([test_currencies[1]])

        account_to_update.save()

        # Retrieve the account from the database
        account = Account.objects.get(pk=account_to_update.pk)
        
        # Check the attributes of the account

        assert account.name == 'Updated Account Name' + str([i])
        assert account.owner == account_to_update.owner
        assert account.co_owners == account_to_update.co_owners
        assert account.description == 'Updated Account Description'
        assert account.type == test_account_types[1]
        assert account.institution == test_institution[1]
        assert [test_currencies[1]] == [currency for currency in account.currencies.all()]
        assert account.wallets == test_accounts[i].wallets
        assert account.created_at == test_accounts[i].created_at
        assert account.updated_at is not None
        assert account.updated_at > account.created_at
        assert timezone.now() - account.updated_at < timezone.timedelta(seconds=1.5)

@pytest.mark.django_db
def test_account_update_wallets_to_no_wallets(test_user, test_account_types, test_account_institution_types, test_institution, test_wallets, test_accounts, test_currencies):
    
    for i in range(0, 2):

        account_to_update = test_accounts[i]
        
        # Update the account
        account_to_update.wallets.set([])

        account_to_update.save()

        # Retrieve the account from the database
        account = Account.objects.get(pk=account_to_update.pk)
        
        # Check the attributes of the account

        assert account.name == account_to_update.name
        assert account.owner == account_to_update.owner
        assert account.co_owners == account_to_update.co_owners
        assert account.description == account_to_update.description
        assert account.type == account_to_update.type
        assert account.institution == account_to_update.institution
        assert account.currencies == account_to_update.currencies
        assert account.wallets.count() == 0
        assert account.created_at == account_to_update.created_at
        assert account.updated_at is not None
        assert account.updated_at > account.created_at
        assert timezone.now() - account.updated_at < timezone.timedelta(seconds=1.5)

@pytest.mark.django_db
def test_account_update_owner(test_user, test_account_types, test_account_institution_types, test_institution, test_wallets, test_accounts, test_currencies):

    account_to_update = test_accounts[0]
    
    for i in range(0, 2):

        account_to_update = test_accounts[i]
        
        # Update the account
        account_to_update.owner = test_user[i+3]

        account_to_update.save()

        # Retrieve the account from the database
        account = Account.objects.get(pk=account_to_update.pk)
        
        # Check the attributes of the account

        assert account.name == account_to_update.name
        assert account.owner == test_user[i+3]
        assert account.co_owners == account_to_update.co_owners
        assert account.description == account_to_update.description
        assert account.type == account_to_update.type
        assert account.institution == account_to_update.institution
        assert account.wallets == account_to_update.wallets
        assert account.created_at == account_to_update.created_at
        assert account.updated_at is not None
        assert account.updated_at > account.created_at
        assert timezone.now() - account.updated_at < timezone.timedelta(seconds=1.5)


@pytest.mark.django_db
def test_account_update_co_owners(test_user, test_account_types, test_account_institution_types, test_institution, test_wallets, test_accounts, test_currencies):

    account_to_update = test_accounts[0]
    
    for i in range(0, 2):

        account_to_update = test_accounts[i]
        
        # Update the account
        account_to_update.co_owners.add(test_user[i+1])

        account_to_update.save()

        # Retrieve the account from the database
        account = Account.objects.get(pk=account_to_update.pk)
        
        # Check the attributes of the account

        assert account.name == account_to_update.name
        assert account.owner == account_to_update.owner
        assert account.co_owners == account_to_update.co_owners
        assert account.description == account_to_update.description
        assert account.type == account_to_update.type
        assert account.institution == account_to_update.institution
        assert account.wallets == account_to_update.wallets
        assert account.created_at == account_to_update.created_at
        assert account.updated_at is not None
        assert account.updated_at > account.created_at
        assert timezone.now() - account.updated_at < timezone.timedelta(seconds=1.5)


@pytest.mark.django_db
def test_account_update_no_owner(test_user, test_account_types, test_account_institution_types, test_institution, test_wallets, test_accounts, test_currencies):
    
        account_to_update = test_accounts[0]
        
        check_account_validations(
            account_to_update=account_to_update,
            name='Updated Account Name',
            owner=None,
            co_owners=None,
            description='Updated Account Description',
            type=test_account_types[1],
            institution=test_institution[1],
            currencies=[test_currencies[1]],
            wallets=[test_wallets[0]],
            error_field='owner',
            error_message="['This field cannot be null.']"
        )

@pytest.mark.django_db
def test_account_update_no_name(test_user, test_account_types, test_account_institution_types, test_institution, test_wallets, test_accounts, test_currencies):

    account_to_update = test_accounts[0]
    
    check_account_validations(
        account_to_update=account_to_update,
        name=None,
        owner=test_user[0],
        co_owners=None,
        description='Updated Account Description',
        type=test_account_types[1],
        institution=test_institution[1],
        currencies=[test_currencies[1]],
        wallets=[test_wallets[0]],
        error_field='name',
        error_message=['This field cannot be null.']
    )

@pytest.mark.django_db
def test_account_update_too_short_name(test_user, test_account_types, test_account_institution_types, test_institution, test_wallets, test_accounts, test_currencies):

    account_to_update = test_accounts[0]
    
    check_account_validations(
        account_to_update=account_to_update,
        name='Ac',
        owner=test_user[0],
        co_owners=None,
        description='Updated Account Description',
        type=test_account_types[1],
        institution=test_institution[1],
        currencies=[test_currencies[1]],
        wallets=[test_wallets[0]],
        error_field='name',
        error_message=['Name must be at least 3 characters long']
    )

@pytest.mark.django_db
def test_account_update_too_long_name(test_user, test_account_types, test_account_institution_types, test_institution, test_wallets, test_accounts, test_currencies):
    
    account_to_update = test_accounts[0]
    
    check_account_validations(
        account_to_update=account_to_update,
        name='A'*101,
        owner=test_user[0],
        co_owners=None,
        description='Updated Account Description',
        type=test_account_types[1],
        institution=test_institution[1],
        currencies=[test_currencies[1]],
        wallets=[test_wallets[0]],
        error_field='name',
        error_message=['Ensure this value has at most 100 characters (it has 101).']
    )

@pytest.mark.django_db
def test_account_update_duplicated_name(test_user, test_account_types, test_account_institution_types, test_institution, test_wallets, test_accounts, test_currencies):
        
    #Prepare data

    first_account = test_accounts[0]
    second_account = test_accounts[1]

    first_account.owner = test_user[0]
    first_account.save()

    second_account.owner = test_user[0]
    second_account.save()


    account_to_update = test_accounts[0]
    
    check_account_validations(
        account_to_update=first_account,
        name=second_account.name,
        owner=test_user[0],
        co_owners=None,
        description='Updated Account Description',
        type=test_account_types[1],
        institution=test_institution[1],
        currencies=[test_currencies[1]],
        wallets=[test_wallets[0]],
        error_field='__all__',
        error_message=['Account with this Owner and Name already exists.']
    )

@pytest.mark.django_db
def test_account_update_too_long_description(test_user, test_account_types, test_account_institution_types, test_institution, test_wallets, test_accounts, test_currencies):
        
    account_to_update = test_accounts[0]
    
    check_account_validations(
        account_to_update=account_to_update,
        name='Updated Account Name',
        owner=test_user[0],
        co_owners=None,
        description='A'*1001,
        type=test_account_types[1],
        institution=test_institution[1],
        currencies=[test_currencies[1]],
        wallets=[test_wallets[0]],
        error_field='description',
        error_message=['Ensure this value has at most 1000 characters (it has 1001).']
    )

@pytest.mark.django_db
def test_account_update_no_type(test_user, test_account_types, test_account_institution_types, test_institution, test_wallets, test_accounts, test_currencies):

    account_to_update = test_accounts[0]
    
    check_account_validations(
        account_to_update=account_to_update,
        name='Updated Account Name',
        owner=test_user[0],
        co_owners=None,
        description='Updated Account Description',
        type=None,
        institution=test_institution[1],
        currencies=[test_currencies[1]],
        wallets=[test_wallets[0]],
        error_field='type',
        error_message=['This field cannot be null.']
    )

@pytest.mark.django_db
def test_account_update_no_institution(test_user, test_account_types, test_account_institution_types, test_institution, test_wallets, test_accounts, test_currencies):
     
    account_to_update = test_accounts[0]
    
    check_account_validations(
        account_to_update=account_to_update,
        name='Updated Account Name',
        owner=test_user[0],
        co_owners=None,
        description='Updated Account Description',
        type=test_account_types[1],
        institution=None,
        currencies=[test_currencies[1]],
        wallets=[test_wallets[0]],
        error_field='institution',
        error_message=['This field cannot be null.']
    )


def check_account_validations(account_to_update, name, owner, co_owners, description, type, institution, currencies, wallets, error_field, error_message, other_account=None):


    with pytest.raises((ValidationError, Account.owner.RelatedObjectDoesNotExist)) as exception_info:

        account_to_update.name = name
        account_to_update.owner = owner
        if co_owners:
            account_to_update.co_owners.set(co_owners)
        account_to_update.description = description
        account_to_update.type = type
        account_to_update.institution = institution
        if currencies:
            account_to_update.currencies.set(currencies)
        if wallets:
            account_to_update.wallets.set(wallets)

        account_to_update.save()


    if exception_info.value.__class__.__name__ == 'RelatedObjectDoesNotExist':
        assert str(exception_info.value) == "Account has no owner."

    else:
        assert exception_info.value.message_dict[error_field] == error_message

        errors = exception_info.value.error_dict[error_field]

        assert len(errors) > 0
        assert error_field in str(exception_info.value)
        assert str(errors[0]) == str(error_message)



        

   


        
