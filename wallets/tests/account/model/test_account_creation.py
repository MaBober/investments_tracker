import pytest

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from wallets.models import Wallet, Account, AccountType, AccountInstitution, AccountInstitutionType
from wallets.tests.test_fixture import test_countries, test_currencies, test_user
from wallets.tests.account.test_fixture import test_account_types, test_account_institution_types, test_institution
from wallets.tests.wallet.test_fixture import test_wallets


@pytest.mark.django_db
def test_account_create_single_owner(test_user, test_account_types, test_institution, test_currencies):
        
    # Create an account for the user
    Account.objects.create(
        name='Test Account',
        type=test_account_types[0],
        institution=test_institution[0],
        owner=test_user[0]
    )
    
    # Check that an Account object has been added to the database
    assert Account.objects.count() == 1

    # Retrieve the account from the database
    account = Account.objects.first()

    # Check the attributes of the account
    assert account.name == 'Test Account'
    assert account.type == test_account_types[0]
    assert account.institution == test_institution[0]
    assert account.owner == test_user[0]
    assert account.co_owners.count() == 0
    assert account.created_at is not None
    assert account.updated_at is not None
    assert account.created_at == account.updated_at
    assert timezone.now() - account.created_at < timezone.timedelta(seconds=1.5)


@pytest.mark.django_db
def test_account_add_multiple_owners(test_user, test_account_types, test_institution, test_currencies):
    
    # Create an account for the user
    account = Account.objects.create(
        name='Test Account',
        type=test_account_types[0],
        institution=test_institution[0],
        owner=test_user[0]
    )
    
    # Add a co-owner to the account
    account.co_owners.add(test_user[1])
    
    # Check that an Account object has been added to the database
    assert Account.objects.count() == 1

    # Retrieve the account from the database
    account = Account.objects.first()

    # Check the attributes of the account
    assert account.name == 'Test Account'
    assert account.type == test_account_types[0]
    assert account.institution == test_institution[0]
    assert account.owner == test_user[0]
    assert account.co_owners.count() == 1
    assert account.co_owners.first() == test_user[1]
    assert account.created_at is not None
    assert account.updated_at is not None
    assert account.created_at == account.updated_at
    assert timezone.now() - account.created_at < timezone.timedelta(seconds=1.5)


@pytest.mark.django_db
def test_account_create_multiple_currencies(test_user, test_account_types, test_institution, test_currencies):
        
    # Create an account for the user
    account = Account.objects.create(
        name='Test Account',
        type=test_account_types[0],
        institution=test_institution[0],
        owner=test_user[0]
    )
    
    account.currencies.add(test_currencies[0])
    account.currencies.add(test_currencies[1])
    
    # Check that an Account object has been added to the database
    assert Account.objects.count() == 1

    # Retrieve the account from the database
    account = Account.objects.first()

    # Check the attributes of the account
    assert account.name == 'Test Account'
    assert account.type == test_account_types[0]
    assert account.institution == test_institution[0]
    assert account.owner == test_user[0]
    assert account.co_owners.count() == 0
    assert account.currencies.count() == 2
    assert account.currencies.first() == test_currencies[0]
    assert account.currencies.last() == test_currencies[1]
    assert account.created_at is not None
    assert account.updated_at is not None
    assert account.created_at == account.updated_at
    assert timezone.now() - account.created_at < timezone.timedelta(seconds=1.5)


@pytest.mark.django_db
def test_account_create_other_instiution(test_user, test_account_types, test_account_institution_types, test_countries, test_currencies):
    
    other_institution = AccountInstitution.objects.create(
        name='Other',
        type=test_account_institution_types[4],
        country=test_countries[0]
    )
    # Create an account for the user
    account = Account.objects.create(
        name='Test Account',
        type=test_account_types[0],
        institution=other_institution,
        other_institution="Dom pana kleksa",
        owner=test_user[0]
    )
     
    # Check that an Account object has been added to the database
    assert Account.objects.count() == 1

    # Retrieve the account from the database
    account = Account.objects.first()

    # Check the attributes of the account
    assert account.name == 'Test Account'
    assert account.type == test_account_types[0]
    assert account.institution.name == 'Other'
    assert account.other_institution == 'Dom pana kleksa'
    assert account.owner == test_user[0]
    assert account.co_owners.count() == 0
    assert account.created_at is not None
    assert account.updated_at is not None
    assert account.created_at == account.updated_at
    assert timezone.now() - account.created_at < timezone.timedelta(seconds=1.5)

@pytest.mark.django_db
def test_account_create_no_owner(test_user, test_account_types, test_institution, test_currencies):
        
    check_account_validations(
        name='Test Account',
        type=test_account_types[0],
        institution=test_institution[0],
        owner=None,
        description='This is a test account',
        error_field='owner',
        error_message=['This field cannot be null.']
    )

@pytest.mark.xfail
@pytest.mark.django_db
def test_account_create_same_owner_and_co_owner(test_user, test_account_types, test_institution, test_currencies):
        
    check_account_validations(
        name='Test Account',
        type=test_account_types[0],
        institution=test_institution[0],
        owner=test_user[0],
        description='This is a test account',
        error_field='__all__',
        error_message=['The owner and co-owner must be different users'],
        co_owners=[test_user[0]]
    )
    

@pytest.mark.django_db
def test_account_create_no_name(test_user, test_account_types, test_institution, test_currencies):
    
    check_account_validations(
        name=None,
        type=test_account_types[0],
        institution=test_institution[0],
        owner=test_user[0],
        description='This is a test account',
        error_field='name',
        error_message=['This field cannot be null.']
    )

@pytest.mark.django_db
def test_account_create_too_long_name(test_user, test_account_types, test_institution, test_currencies):
     
    check_account_validations(
        name='A'*101,
        type=test_account_types[0],
        institution=test_institution[0],
        owner=test_user[0],
        description='This is a test account',
        error_field='name',
        error_message=['Ensure this value has at most 100 characters (it has 101).']
    )

@pytest.mark.django_db
def test_account_create_too_short_name(test_user, test_account_types, test_institution, test_currencies):
        
    check_account_validations(
        name='A',
        type=test_account_types[0],
        institution=test_institution[0],
        owner=test_user[0],
        description='This is a test account',
        error_field='name',
        error_message=['Name must be at least 3 characters long']
    )

@pytest.mark.django_db
def test_account_create_duplicated_name(test_user, test_account_types, test_institution, test_currencies):
             
    # Create an account for the user
    Account.objects.create(
        name='Test Account',
        type=test_account_types[0],
        institution=test_institution[0],
        owner=test_user[0]
    )

    assert Account.objects.count() == 1

    check_account_validations(
        name='Test Account',
        type=test_account_types[0],
        institution=test_institution[0],
        owner=test_user[0],
        description='This is a test account',
        error_field='__all__',
        error_message=['Account with this Owner and Name already exists.'],
        other_wallets=1
    )

@pytest.mark.django_db
def test_account_create_too_long_description(test_user, test_account_types, test_institution, test_currencies):
        
    check_account_validations(
        name='Test Account',
        type=test_account_types[0],
        institution=test_institution[0],
        owner=test_user[0],
        description='A'*1001,
        error_field='description',
        error_message=['Ensure this value has at most 1000 characters (it has 1001).']
    )

@pytest.mark.django_db
def test_account_create_no_type(test_user, test_account_types, test_institution, test_currencies):
        
    check_account_validations(
        name='Test Account',
        type=None,
        institution=test_institution[0],
        owner=test_user[0],
        description='This is a test account',
        error_field='type',
        error_message=['This field cannot be null.']
    )

@pytest.mark.django_db
def test_account_create_no_institution(test_user, test_account_types, test_institution, test_currencies):
        
    check_account_validations(
        name='Test Account',
        type=test_account_types[0],
        institution=None,
        owner=test_user[0],
        description='This is a test account',
        error_field='institution',
        error_message=['This field cannot be null.']
    )

@pytest.mark.django_db
def test_account_create_add_wallet(test_user, test_account_types, test_institution, test_currencies, test_wallets):

    # Create an account for the user
    account = Account.objects.create(
        name='Test Account',
        type=test_account_types[0],
        institution=test_institution[0],
        owner=test_user[0],
    )
    
    # Check that an Account object has been added to the database
    assert Account.objects.count() == 1

    account.wallets.add(test_wallets[0])

    # Retrieve the account from the database
    account = Account.objects.first()

    # Check the attributes of the account
    assert account.name == 'Test Account'
    assert account.type == test_account_types[0]
    assert account.institution == test_institution[0]
    assert account.owner == test_user[0]
    assert account.co_owners.count() == 0
    assert account.wallets.first() == test_wallets[0]
    assert account.created_at is not None
    assert account.updated_at is not None
    assert account.created_at == account.updated_at
    assert timezone.now() - account.created_at < timezone.timedelta(seconds=1.5)


@pytest.mark.xfail
@pytest.mark.django_db
def test_account_create_with_wallet_not_owned_by_user(test_user, test_account_types, test_institution, test_currencies, test_wallets):

    check_account_validations(
        name='Test Account',
        type=test_account_types[0],
        institution=test_institution[0],
        owner=test_user[0],
        description='This is a test account',
        error_field='wallets',
        error_message=['Account wallets must be owned by the account owner.'],
        wallets=[test_wallets[2]]   
    )       


@pytest.mark.django_db
def test_account_create_with_instituion_selecteded_and_other_institution(test_user, test_account_types, test_institution, test_account_institution_types, test_countries, test_currencies):

    check_account_validations(
        name='Test Account',
        type=test_account_types[0],
        institution=test_institution[0],
        owner=test_user[0],
        description='This is a test account',
        error_field='__all__',
        error_message=['Other institution field must be blank if institution is selected.'],
        other_institution='Dom pana kleksa'
    )


@pytest.mark.django_db
def test_account_create_with_other_institution_selecteded_and_no_other_institution(test_user, test_account_types, test_account_institution_types, test_countries, test_currencies):

    other_institution = AccountInstitution.objects.create(
        name='Other',
        type=test_account_institution_types[4],
        country=test_countries[0]
    )

    check_account_validations(
        name='Test Account',
        type=test_account_types[0],
        institution=other_institution,
        owner=test_user[0],
        description='This is a test account',
        error_field='__all__',
        error_message=['Other institution field must not be blank if Other institution is selected.'],
        other_institution=''
    )



def check_account_validations(name, type, institution, owner, description, error_field, error_message, other_wallets = 0, co_owners =[], wallets=[], currencies=[], other_institution=''):

    with pytest.raises(ValidationError) as exception_info:
        account = Account.objects.create(
            name=name,
            type=type,
            institution=institution,
            owner=owner,
            description=description,
            other_institution=other_institution
        )

        if wallets:
            for wallet in wallets:
                account.wallets.add(wallet)

        if co_owners:
            for co_owner in co_owners:
                account.co_owners.add(co_owner)
        
        if currencies:
            for currency in currencies:
                account.currencies.add(currency)        
    

    assert Account.objects.count() == other_wallets
    assert exception_info.value.message_dict[error_field] == error_message

    errors = exception_info.value.error_dict[error_field]

    assert len(errors) > 0
    assert error_field in str(exception_info.value)
    assert str(errors[0]) == str(error_message)

    assert Account.objects.count() == other_wallets
