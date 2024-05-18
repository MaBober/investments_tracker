import pytest

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.db import transaction
from django.utils import timezone

from wallets.models import  AccountType, AccountInstitutionType, AccountInstitution

from wallets.tests.test_fixture import test_currencies, test_countries
from wallets.tests.account.test_fixture import test_account_types, test_account_institution_types

@pytest.mark.django_db
def test_account_type_create():

    AccountType.objects.create(name='Test Account Type')
    
    assert AccountType.objects.count() == 1
    
    account_type = AccountType.objects.first()
    
    assert account_type.name == 'Test Account Type'
    assert account_type.description == ''
    assert account_type.created_at is not None
    assert account_type.updated_at is not None
    assert account_type.created_at == account_type.updated_at
    assert timezone.now() - account_type.created_at < timezone.timedelta(seconds=1.5)

@pytest.mark.django_db
def test_account_type_create_with_description():

    AccountType.objects.create(name='Test Account Type', description='This is a test account type')
    
    assert AccountType.objects.count() == 1
    
    account_type = AccountType.objects.first()
    
    assert account_type.name == 'Test Account Type'
    assert account_type.description == 'This is a test account type'
    assert account_type.created_at is not None
    assert account_type.updated_at is not None
    assert account_type.created_at == account_type.updated_at
    assert timezone.now() - account_type.created_at < timezone.timedelta(seconds=1.5)

@pytest.mark.django_db
def test_account_type_create_duplicate_name():

    AccountType.objects.create(name='Test Account Type')
    
    with pytest.raises(ValidationError) as exception_info:
        AccountType.objects.create(name='Test Account Type')

    assert exception_info.value.error_dict.get('name') != None
    assert str(exception_info.value.error_dict.get('name')[0]) == "['Account type with this Name already exists.']"

    assert AccountType.objects.count() == 1

@pytest.mark.django_db
def test_account_type_create_empty_name():

    with pytest.raises(ValidationError) as exception_info:
        AccountType.objects.create(name='')

    assert exception_info.value.error_dict.get('name') != None
    assert str(exception_info.value.error_dict.get('name')[0]) == "['This field cannot be blank.']"

    assert AccountType.objects.count() == 0

@pytest.mark.django_db
def test_account_type_create_name_too_long():

    with pytest.raises(ValidationError) as exception_info:
        AccountType.objects.create(name='A' * 101)

    assert exception_info.value.error_dict.get('name') != None
    assert str(exception_info.value.error_dict.get('name')[0]) == "['Ensure this value has at most 100 characters (it has 101).']"

    assert AccountType.objects.count() == 0

@pytest.mark.django_db
def test_account_type_update():

    account_type = AccountType.objects.create(name='Test Account Type')
    
    account_type.name = 'Updated Account Type'
    account_type.description = 'This is an updated account type'
    account_type.save()
    
    assert AccountType.objects.count() == 1
    
    account_type = AccountType.objects.first()
    
    assert account_type.name == 'Updated Account Type'
    assert account_type.description == 'This is an updated account type'
    assert account_type.created_at is not None
    assert account_type.updated_at is not None
    assert account_type.created_at != account_type.updated_at
    assert timezone.now() - account_type.updated_at < timezone.timedelta(seconds=1.5)

@pytest.mark.django_db
def test_account_type_update_to_duplicate_name():

    AccountType.objects.create(name='Test Account Type')
    account_type = AccountType.objects.create(name='Another Account Type')
    
    account_type.name = 'Test Account Type'
    
    with pytest.raises(ValidationError) as exception_info:
        account_type.save()

    assert exception_info.value.error_dict.get('name') != None
    assert str(exception_info.value.error_dict.get('name')[0]) == "['Account type with this Name already exists.']"
    
    assert AccountType.objects.count() == 2
    assert AccountType.objects.filter(name='Test Account Type').count() == 1
    assert AccountType.objects.filter(name='Another Account Type').count() == 1

@pytest.mark.django_db
def test_account_type_update_to_empty_name():

    account_type = AccountType.objects.create(name='Test Account Type')
    
    account_type.name = ''
    
    with pytest.raises(ValidationError) as exception_info:
        account_type.save()

    assert exception_info.value.error_dict.get('name') != None
    assert str(exception_info.value.error_dict.get('name')[0]) == "['This field cannot be blank.']"
    
    assert AccountType.objects.count() == 1
    assert AccountType.objects.filter(name='Test Account Type').count() == 1

@pytest.mark.django_db
def test_account_type_update_to_name_too_long():

    account_type = AccountType.objects.create(name='Test Account Type')
    
    account_type.name = 'A' * 101
    
    with pytest.raises(ValidationError) as exception_info:
        account_type.save()
    
    assert exception_info.value.error_dict.get('name') != None
    assert str(exception_info.value.error_dict.get('name')[0]) == "['Ensure this value has at most 100 characters (it has 101).']"

    assert AccountType.objects.count() == 1
    assert AccountType.objects.filter(name='Test Account Type').count() == 1

@pytest.mark.django_db
def test_account_institution_type_create():

    AccountInstitutionType.objects.create(name='Test Account Institution Type')
    
    assert AccountInstitutionType.objects.count() == 1
    
    account_institution_type = AccountInstitutionType.objects.first()
    
    assert account_institution_type.name == 'Test Account Institution Type'
    assert account_institution_type.description == ''
    assert account_institution_type.created_at is not None
    assert account_institution_type.updated_at is not None
    assert account_institution_type.created_at == account_institution_type.updated_at
    assert timezone.now() - account_institution_type.created_at < timezone.timedelta(seconds=1.5)


@pytest.mark.django_db
def test_account_institution_type_create_with_description():

    AccountInstitutionType.objects.create(name='Test Account Institution Type', description='This is a test account institution type')
    
    assert AccountInstitutionType.objects.count() == 1
    
    account_institution_type = AccountInstitutionType.objects.first()
    
    assert account_institution_type.name == 'Test Account Institution Type'
    assert account_institution_type.description == 'This is a test account institution type'
    assert account_institution_type.created_at is not None
    assert account_institution_type.updated_at is not None
    assert account_institution_type.created_at == account_institution_type.updated_at
    assert timezone.now() - account_institution_type.created_at < timezone.timedelta(seconds=1.5)

@pytest.mark.django_db
def test_account_institution_type_create_duplicate_name():

    AccountInstitutionType.objects.create(name='Test Account Institution Type')
    
    with pytest.raises(ValidationError) as exception_info:
        AccountInstitutionType.objects.create(name='Test Account Institution Type')

    assert exception_info.value.error_dict.get('name') != None
    assert str(exception_info.value.error_dict.get('name')[0]) == "['Account institution type with this Name already exists.']"

    assert AccountInstitutionType.objects.count() == 1

@pytest.mark.django_db
def test_account_institution_type_create_empty_name():

    with pytest.raises(ValidationError) as exception_info:
        AccountInstitutionType.objects.create(name='')

    assert exception_info.value.error_dict.get('name') != None
    assert str(exception_info.value.error_dict.get('name')[0]) == "['This field cannot be blank.']"

    assert AccountInstitutionType.objects.count() == 0

@pytest.mark.django_db
def test_account_institution_type_create_name_too_long():

    with pytest.raises(ValidationError) as exception_info:
        AccountInstitutionType.objects.create(name='A' * 101)

    assert exception_info.value.error_dict.get('name') != None
    assert str(exception_info.value.error_dict.get('name')[0]) == "['Ensure this value has at most 100 characters (it has 101).']"

    assert AccountInstitutionType.objects.count() == 0

@pytest.mark.django_db
def test_account_institution_type_update():

    account_institution_type = AccountInstitutionType.objects.create(name='Test Account Institution Type')
    
    account_institution_type.name = 'Updated Account Institution Type'
    account_institution_type.description = 'This is an updated account institution type'
    account_institution_type.save()
    
    assert AccountInstitutionType.objects.count() == 1
    
    account_institution_type = AccountInstitutionType.objects.first()
    
    assert account_institution_type.name == 'Updated Account Institution Type'
    assert account_institution_type.description == 'This is an updated account institution type'
    assert account_institution_type.created_at is not None
    assert account_institution_type.updated_at is not None
    assert account_institution_type.created_at != account_institution_type.updated_at
    assert timezone.now() - account_institution_type.updated_at < timezone.timedelta(seconds=1.5)

@pytest.mark.django_db
def test_account_institution_type_update_to_duplicate_name():

    AccountInstitutionType.objects.create(name='Test Account Institution Type')
    account_institution_type = AccountInstitutionType.objects.create(name='Another Account Institution Type')
    
    account_institution_type.name = 'Test Account Institution Type'
    
    with pytest.raises(ValidationError) as exception_info:
        account_institution_type.save()

    assert exception_info.value.error_dict.get('name') != None
    assert str(exception_info.value.error_dict.get('name')[0]) == "['Account institution type with this Name already exists.']"
    
    assert AccountInstitutionType.objects.count() == 2
    assert AccountInstitutionType.objects.filter(name='Test Account Institution Type').count() == 1
    assert AccountInstitutionType.objects.filter(name='Another Account Institution Type').count() == 1

@pytest.mark.django_db
def test_account_institution_type_update_to_empty_name():

    account_institution_type = AccountInstitutionType.objects.create(name='Test Account Institution Type')
    
    account_institution_type.name = ''
    
    with pytest.raises(ValidationError) as exception_info:
        account_institution_type.save()

    assert exception_info.value.error_dict.get('name') != None
    assert str(exception_info.value.error_dict.get('name')[0]) == "['This field cannot be blank.']"
    
    assert AccountInstitutionType.objects.count() == 1
    assert AccountInstitutionType.objects.filter(name='Test Account Institution Type').count() == 1

@pytest.mark.django_db
def test_account_institution_type_update_to_name_too_long():

    account_institution_type = AccountInstitutionType.objects.create(name='Test Account Institution Type')
    
    account_institution_type.name = 'A' * 101
    
    with pytest.raises(ValidationError) as exception_info:
        account_institution_type.save()
    
    assert exception_info.value.error_dict.get('name') != None
    assert str(exception_info.value.error_dict.get('name')[0]) == "['Ensure this value has at most 100 characters (it has 101).']"

    assert AccountInstitutionType.objects.count() == 1
    assert AccountInstitutionType.objects.filter(name='Test Account Institution Type').count() == 1

@pytest.mark.django_db
def test_account_institution_create(test_account_institution_types, test_countries):
    
        AccountInstitution.objects.create(name='Test Account Institution', type=test_account_institution_types[0], country=test_countries[0])

        assert AccountInstitution.objects.count() == 1

        account_institution = AccountInstitution.objects.first()
        
        assert account_institution.name == 'Test Account Institution'
        assert account_institution.type == test_account_institution_types[0]
        assert account_institution.country == test_countries[0]
        assert account_institution.description == ''
        assert account_institution.created_at is not None
        assert account_institution.updated_at is not None
        assert account_institution.created_at == account_institution.updated_at
        assert timezone.now() - account_institution.created_at < timezone.timedelta(seconds=1.5)



@pytest.mark.django_db
def test_account_institution_create_with_description(test_account_institution_types, test_countries):
    
        AccountInstitution.objects.create(name='Test Account Institution', type=test_account_institution_types[0], country=test_countries[0], description='This is a test account institution')
        
        assert AccountInstitution.objects.count() == 1
        
        account_institution = AccountInstitution.objects.first()
        
        assert account_institution.name == 'Test Account Institution'
        assert account_institution.type == test_account_institution_types[0]
        assert account_institution.country == test_countries[0]
        assert account_institution.description == 'This is a test account institution'
        assert account_institution.created_at is not None
        assert account_institution.updated_at is not None
        assert account_institution.created_at == account_institution.updated_at
        assert timezone.now() - account_institution.created_at < timezone.timedelta(seconds=1.5)

@pytest.mark.django_db
def test_account_institution_create_duplicate_name(test_account_institution_types, test_countries):

        AccountInstitution.objects.create(name='Test Account Institution', type=test_account_institution_types[0], country=test_countries[0])
        
        with pytest.raises(ValidationError) as exception_info:
            AccountInstitution.objects.create(name='Test Account Institution', type=test_account_institution_types[0], country=test_countries[0])

        assert exception_info.value.error_dict.get('name') != None
        assert str(exception_info.value.error_dict.get('name')[0]) == "['Account institution with this Name already exists.']"

        assert AccountInstitution.objects.count() == 1

@pytest.mark.django_db
def test_account_institution_create_empty_name(test_account_institution_types, test_countries):

        with pytest.raises(ValidationError) as exception_info:
            AccountInstitution.objects.create(name='', type=test_account_institution_types[0], country=test_countries[0])

        assert exception_info.value.error_dict.get('name') != None
        assert str(exception_info.value.error_dict.get('name')[0]) == "['This field cannot be blank.']"

        assert AccountInstitution.objects.count() == 0

@pytest.mark.django_db
def test_account_institution_create_name_too_long(test_account_institution_types, test_countries):

        with pytest.raises(ValidationError) as exception_info:
            AccountInstitution.objects.create(name='A' * 101, type=test_account_institution_types[0], country=test_countries[0])

        assert exception_info.value.error_dict.get('name') != None
        assert str(exception_info.value.error_dict.get('name')[0]) == "['Ensure this value has at most 100 characters (it has 101).']"

        assert AccountInstitution.objects.count() == 0

@pytest.mark.django_db
def test_account_institution_create_empty_country(test_account_institution_types):

        with pytest.raises(ValidationError) as exception_info:
            AccountInstitution.objects.create(name='Test Account Institution', type=test_account_institution_types[0])

        assert exception_info.value.error_dict.get('country') != None
        assert str(exception_info.value.error_dict.get('country')[0]) == "['This field cannot be null.']"

        assert AccountInstitution.objects.count() == 0

@pytest.mark.django_db
def test_account_institution_create_country_non_existing(test_account_institution_types):

        with pytest.raises(ValueError) as exception_info:
            AccountInstitution.objects.create(name='Test Account Institution', type=test_account_institution_types[0], country="Non Existing Country")

        assert str(exception_info.value) == 'Cannot assign "\'Non Existing Country\'": "AccountInstitution.country" must be a "Country" instance.'

        assert AccountInstitution.objects.count() == 0

@pytest.mark.django_db
def test_account_create_description_too_long(test_account_institution_types, test_countries):
         
            with pytest.raises(ValidationError) as exception_info:
                AccountInstitution.objects.create(name='Test Account Institution', type=test_account_institution_types[0], country=test_countries[0], description='A' * 1001)
    
            assert exception_info.value.error_dict.get('description') != None
            assert str(exception_info.value.error_dict.get('description')[0]) == "['Ensure this value has at most 1000 characters (it has 1001).']"
    
            assert AccountInstitution.objects.count() == 0


@pytest.mark.django_db
def test_account_institution_update(test_account_institution_types, test_countries):

        account_institution = AccountInstitution.objects.create(name='Test Account Institution', type=test_account_institution_types[0], country=test_countries[0])
        
        account_institution.name = 'Updated Account Institution'
        account_institution.type = test_account_institution_types[1]
        account_institution.country = test_countries[1]
        account_institution.description = 'This is an updated account institution'
        account_institution.save()
        
        assert AccountInstitution.objects.count() == 1
        
        account_institution = AccountInstitution.objects.first()
        
        assert account_institution.name == 'Updated Account Institution'
        assert account_institution.type == test_account_institution_types[1]
        assert account_institution.country == test_countries[1]
        assert account_institution.description == 'This is an updated account institution'
        assert account_institution.created_at is not None
        assert account_institution.updated_at is not None
        assert account_institution.created_at != account_institution.updated_at
        assert timezone.now() - account_institution.updated_at < timezone.timedelta(seconds=1.5)

@pytest.mark.django_db
def test_account_institution_update_to_duplicate_name(test_account_institution_types, test_countries):

        AccountInstitution.objects.create(name='Test Account Institution', type=test_account_institution_types[0], country=test_countries[0])
        account_institution = AccountInstitution.objects.create(name='Another Account Institution', type=test_account_institution_types[1], country=test_countries[0])
        
        account_institution.name = 'Test Account Institution'
        
        with pytest.raises(ValidationError) as exception_info:
            account_institution.save()

        assert exception_info.value.error_dict.get('name') != None
        assert str(exception_info.value.error_dict.get('name')[0]) == "['Account institution with this Name already exists.']"
        
        assert AccountInstitution.objects.count() == 2
        assert AccountInstitution.objects.filter(name='Test Account Institution').count() == 1
        assert AccountInstitution.objects.filter(name='Another Account Institution').count() == 1

@pytest.mark.django_db
def test_account_institution_update_to_empty_name(test_account_institution_types, test_countries):

        account_institution = AccountInstitution.objects.create(name='Test Account Institution', type=test_account_institution_types[0], country=test_countries[0])
        
        account_institution.name = ''
        
        with pytest.raises(ValidationError) as exception_info:
            account_institution.save()

        assert exception_info.value.error_dict.get('name') != None
        assert str(exception_info.value.error_dict.get('name')[0]) == "['This field cannot be blank.']"
        
        assert AccountInstitution.objects.count() == 1
        assert AccountInstitution.objects.filter(name='Test Account Institution').count() == 1

@pytest.mark.django_db
def test_account_institution_update_to_name_too_long(test_account_institution_types, test_countries):

        account_institution = AccountInstitution.objects.create(name='Test Account Institution', type=test_account_institution_types[0], country=test_countries[0])
        
        account_institution.name = 'A' * 101
        
        with pytest.raises(ValidationError) as exception_info:
            account_institution.save()
        
        assert exception_info.value.error_dict.get('name') != None
        assert str(exception_info.value.error_dict.get('name')[0]) == "['Ensure this value has at most 100 characters (it has 101).']"

        assert AccountInstitution.objects.count() == 1
        assert AccountInstitution.objects.filter(name='Test Account Institution').count() == 1

@pytest.mark.django_db
def test_account_institution_update_to_empty_country(test_account_institution_types, test_countries):

        account_institution = AccountInstitution.objects.create(name='Test Account Institution', type=test_account_institution_types[0], country=test_countries[0])
        
        account_institution.country = None
        
        with pytest.raises(ValidationError) as exception_info:
            account_institution.save()

        assert exception_info.value.error_dict.get('country') != None
        assert str(exception_info.value.error_dict.get('country')[0]) == "['This field cannot be null.']"
        
        assert AccountInstitution.objects.count() == 1
        assert AccountInstitution.objects.filter(name='Test Account Institution').count() == 1

@pytest.mark.django_db
def test_account_institution_update_to_country_non_existing(test_account_institution_types, test_countries):

        account_institution = AccountInstitution.objects.create(name='Test Account Institution', type=test_account_institution_types[0], country=test_countries[0])
        
        with pytest.raises(ValueError) as exception_info:
            account_institution.country = "Non Existing Country"
            account_institution.save()

        assert str(exception_info.value) == 'Cannot assign "\'Non Existing Country\'": "AccountInstitution.country" must be a "Country" instance.'

        assert AccountInstitution.objects.count() == 1
        assert AccountInstitution.objects.filter(name='Test Account Institution').count() == 1

@pytest.mark.django_db
def test_account_institution_update_description_too_long(test_account_institution_types, test_countries):

        account_institution = AccountInstitution.objects.create(name='Test Account Institution', type=test_account_institution_types[0], country=test_countries[0])
        
        account_institution.description = 'A' * 1001
        
        with pytest.raises(ValidationError) as exception_info:
            account_institution.save()
    
        assert exception_info.value.error_dict.get('description') != None
        assert str(exception_info.value.error_dict.get('description')[0]) == "['Ensure this value has at most 1000 characters (it has 1001).']"
    
        assert AccountInstitution.objects.count() == 1
        assert AccountInstitution.objects.filter(name='Test Account Institution').count() == 1




    

    




    