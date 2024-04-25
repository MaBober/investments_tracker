import pytest
from pprint import pprint

from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APIClient

from wallets.tests.test_fixture import test_user, authenticated_client, api_client, admin_logged_client, api_url, test_countries, test_currencies
from wallets.tests.wallet.test_fixture import test_wallets
from wallets.tests.account.test_fixture import test_accounts, test_account_institution_types, test_account_types, test_institution

from wallets.models import Wallet
from wallets.models import Account

@pytest.mark.django_db
def test_get_accounts(admin_logged_client, test_accounts):

    response = admin_logged_client.get(api_url('accounts/'))
    
    assert response.status_code == 200
    print(response.data)
    assert response.data['count'] == len(test_accounts)
    assert response.data['results'][0]['name'] == test_accounts[0].name
    assert response.data['results'][0]['description'] == test_accounts[0].description
    assert response.data['results'][0]['owner_id'] == str(test_accounts[0].owner.id)
    assert response.data['results'][0]['wallets'] == [wallet.id for wallet in test_accounts[0].wallets.all()]
    assert response.data['results'][0]['type'] == test_accounts[0].type.name
    assert response.data['results'][0]['institution'] == test_accounts[0].institution.name
    assert response.data['results'][0]['currencies'] == [currency.code for currency in test_accounts[0].currencies.all()]
    assert response.data['results'][0]['created_at'] == test_accounts[0].created_at.astimezone(timezone.get_current_timezone()).isoformat()
    assert response.data['results'][0]['updated_at'] == test_accounts[0].updated_at.astimezone(timezone.get_current_timezone()).isoformat()

    
@pytest.mark.django_db
def test_get_accounts_no_auth(api_client):

    response = api_client.get(api_url('accounts/'))
    
    assert response.status_code == 401
    assert response.data['detail'] == 'Authentication credentials were not provided.'


@pytest.mark.django_db
def test_get_account_no_admin(authenticated_client, test_accounts):

    response = authenticated_client.get(api_url('accounts/'))
    
    assert response.status_code == 403
    assert response.data.get('detail') == 'You do not have permission to perform this action.'


@pytest.mark.django_db
def test_get_single_account_owner(api_client, test_user, test_accounts):
    
    account_to_test = test_accounts[0]
    api_client.force_authenticate(user=account_to_test.owner)

    response = api_client.get(api_url(f'accounts/{account_to_test.id}/'))

    assert response.status_code == 200
    assert response.data['name'] == account_to_test.name
    assert response.data['description'] == account_to_test.description
    assert response.data['owner_id'] == str(account_to_test.owner.id)
    assert response.data['wallets'] == [wallet.id for wallet in account_to_test.wallets.all()]
    assert response.data['type'] == account_to_test.type.name
    assert response.data['institution'] == account_to_test.institution.name
    assert response.data['currencies'] == [currency.code for currency in account_to_test.currencies.all()]
    assert response.data['created_at'] == account_to_test.created_at.astimezone(timezone.get_current_timezone()).isoformat()
    assert response.data['updated_at'] == account_to_test.updated_at.astimezone(timezone.get_current_timezone()).isoformat()


@pytest.mark.django_db
def test_get_single_account_co_owner(api_client, test_user, test_accounts):

    account_to_test = test_accounts[0]

    #Prepare data
    account_to_test.co_owners.clear()
    account_to_test.co_owners.add(test_user[3])
    account_to_test.save()

    api_client.force_authenticate(user=account_to_test.co_owners.all()[0])

    response = api_client.get(api_url(f'accounts/{account_to_test.id}/'))

    assert response.status_code == 200
    assert response.data['name'] == account_to_test.name
    assert response.data['description'] == account_to_test.description
    assert response.data['owner_id'] == str(account_to_test.owner.id)
    assert response.data['wallets'] == [wallet.id for wallet in account_to_test.wallets.all()]
    assert response.data['type'] == account_to_test.type.name
    assert response.data['institution'] == account_to_test.institution.name
    assert response.data['currencies'] == [currency.code for currency in account_to_test.currencies.all()]
    assert response.data['created_at'] == account_to_test.created_at.astimezone(timezone.get_current_timezone()).isoformat()
    assert response.data['updated_at'] == account_to_test.updated_at.astimezone(timezone.get_current_timezone()).isoformat()


@pytest.mark.django_db
def test_get_single_account_no_auth(api_client, test_accounts):
    
    account_to_test = test_accounts[0]

    response = api_client.get(api_url(f'accounts/{account_to_test.id}/'))

    assert response.status_code == 401
    assert response.data['detail'] == 'Authentication credentials were not provided.'


@pytest.mark.django_db
def test_get_single_account_nor_owner_or_co_owner(api_client, test_user, test_accounts):
    
    account_to_test = test_accounts[0]

    #Prepare data
    account_to_test.co_owners.clear()
    account_to_test.save()

    for user in test_user:
        if user != account_to_test.owner:
            user_to_test = user
            break

    api_client.force_authenticate(user=user_to_test)

    response = api_client.get(api_url(f'accounts/{account_to_test.id}/'))

    assert response.status_code == 403
    assert response.data.get('detail') == 'You do not have permission to perform this action.'


@pytest.mark.django_db
def test_get_single_account_not_found(api_client, test_user, test_accounts):
    
    response = api_client.get(api_url(f'accounts/100/'))

    assert response.status_code == 404
    assert response.data.get('detail') == 'No Account matches the given query.'


@pytest.mark.django_db
def test_create_account(authenticated_client, test_user, test_wallets, test_account_types, test_account_institution_types, test_institution, test_currencies):
    
    data = {
        "name": "Checking Account",
        "type": test_account_types[0].name,
        "institution": test_institution[0].name,
        "currencies": [test_currencies[0].code, test_currencies[1].code],
        "description": "Checking account description",
        "owner": test_user[0].id,
        "co_owners": [test_user[1].id, test_user[2].id]
    }

    response = authenticated_client.post(api_url('accounts/'), data=data)

    assert response.status_code == 201
    assert response.data['name'] == data['name']
    assert response.data['description'] == data['description']
    assert response.data['owner_id'] == data['owner']
    assert response.data['type'] == test_account_types[0].name
    assert response.data['institution'] == test_institution[0].name
    assert response.data['currencies'] == data['currencies']

@pytest.mark.django_db
def test_create_account_add_owned_wallet(authenticated_client, test_user, test_wallets, test_account_types, test_account_institution_types, test_institution, test_currencies):
    
    #Prepare data
    test_wallets[0].owner = test_user[0]
    test_wallets[0].co_owners.clear()
    test_wallets[0].save()

    data = {
        "name": "Checking Account",
        "type": test_account_types[0].name,
        "institution": test_institution[0].name,
        "currencies":[ test_currencies[0].code],
        "wallets": [test_wallets[0].id],
        "description": "Checking account description",
        "owner": test_user[0].id,
        "co_owners": [test_user[1].id, test_user[2].id]
    }

    response = authenticated_client.post(api_url('accounts/'), data=data)

    assert response.status_code == 201
    assert response.data['name'] == data['name']
    assert response.data['description'] == data['description']
    assert response.data['owner_id'] == data['owner']
    assert response.data['wallets'] == data['wallets']
    assert response.data['type'] == test_account_types[0].name
    assert response.data['institution'] == test_institution[0].name
    assert response.data['currencies'] == data['currencies']


@pytest.mark.django_db    
def test_create_account_add_co_owned_wallet(authenticated_client, test_user, test_wallets, test_account_types, test_account_institution_types, test_institution, test_currencies):
    
    #Prepare data
    test_wallets[0].owner = test_user[1]
    test_wallets[0].co_owners.clear()
    test_wallets[0].co_owners.add(test_user[0])
    test_wallets[0].save()

    data = {
        "name": "Checking Account",
        "type": test_account_types[0].name,
        "institution": test_institution[0].name,
        "currencies": [test_currencies[0].code],
        "wallets": [test_wallets[0].id],
        "description": "Checking account description",
        "owner": test_user[0].id,
        "co_owners": [test_user[1].id, test_user[2].id]
    }

    response = authenticated_client.post(api_url('accounts/'), data=data)

    assert response.status_code == 201
    assert response.data['name'] == data['name']
    assert response.data['description'] == data['description']
    assert response.data['owner_id'] == data['owner']
    assert response.data['wallets'] == data['wallets']
    assert response.data['type'] == test_account_types[0].name
    assert response.data['institution'] == test_institution[0].name
    assert response.data['currencies'] == data['currencies']

@pytest.mark.django_db
def test_create_account_other_institution(authenticated_client, test_user, test_wallets, test_account_types, test_account_institution_types, test_institution, test_currencies):
        
    data = {
        "name": "Checking Account",
        "type": test_account_types[0].name,
        "institution": "Other",
        "other_institution": "Other Institution",
        "currencies": [test_currencies[0].code],
        "wallets": [test_wallets[0].id],
        "description": "Checking account description",
        "owner": test_user[0].id,
        "co_owners": [test_user[1].id, test_user[2].id]
    }

    response = authenticated_client.post(api_url('accounts/'), data=data)

    assert response.status_code == 201
    assert response.data['name'] == data['name']
    assert response.data['description'] == data['description']
    assert response.data['owner_id'] == data['owner']
    assert response.data['wallets'] == data['wallets']
    assert response.data['type'] == test_account_types[0].name
    assert response.data['institution'] == "Other"
    assert response.data['other_institution'] == data['other_institution']
    assert response.data['currencies'] == data['currencies']

@pytest.mark.django_db
def test_create_account_other_institution_no_other(authenticated_client, test_user, test_wallets, test_account_types, test_account_institution_types, test_institution, test_currencies):
            
    data = {
        "name": "Checking Account",
        "type": test_account_types[0].name,
        "institution": "Other",
        "currencies": [test_currencies[0].code],
        "wallets": [test_wallets[0].id],
        "description": "Checking account description",
        "owner": test_user[0].id,
        "co_owners": [test_user[1].id, test_user[2].id]
    }

    check_account_create_validation(authenticated_client,
                                    data=data,
                                    error_field='other_institution',
                                    error_message='This field cannot be empty if institution is set to "Other".',
                                    other_wallets=Account.objects.count())
    
@pytest.mark.django_db
def test_create_account_other_institution_other_empty_string(authenticated_client, test_user, test_wallets, test_account_types, test_account_institution_types, test_institution, test_currencies):
            
    data = {
        "name": "Checking Account",
        "type": test_account_types[0].name,
        "institution": "Other",
        "other_institution": "",
        "currencies": [test_currencies[0].code],
        "wallets": [test_wallets[0].id],
        "description": "Checking account description",
        "owner": test_user[0].id,
        "co_owners": [test_user[1].id, test_user[2].id]
    }

    check_account_create_validation(authenticated_client,
                                    data=data,
                                    error_field='other_institution',
                                    error_message='This field cannot be empty if institution is set to "Other".',
                                    other_wallets=Account.objects.count()
    )

@pytest.mark.django_db
def test_create_account_institution_selected_and_other(authenticated_client, test_user, test_wallets, test_account_types, test_account_institution_types, test_institution, test_currencies):
            
    data = {
        "name": "Checking Account",
        "type": test_account_types[0].name,
        "institution": test_institution[0].name,
        "other_institution": "Other Institution",
        "currencies": [test_currencies[0].code],
        "wallets": [test_wallets[0].id],
        "description": "Checking account description",
        "owner": test_user[0].id,
        "co_owners": [test_user[1].id, test_user[2].id]
    }

    check_account_create_validation(authenticated_client,
                                    data=data,
                                    error_field='other_institution',
                                    error_message="This field must be empty if institution is not set to 'Other'.",
                                    other_wallets=Account.objects.count())


@pytest.mark.django_db
def test_create_account_no_auth(api_client, test_user, test_wallets, test_account_types, test_account_institution_types, test_institution, test_currencies):
    
    data = {
        "name": "Checking Account",
        "type": test_account_types[0].name,
        "institution": test_institution[0].name,
        "currencies": [test_currencies[0].code],
        "wallets": [test_wallets[0].id],
        "description": "Checking account description",
        "owner": test_user[0].id,
        "co_owners": [test_user[1].id, test_user[2].id]
    }

    response = api_client.post(api_url('accounts/'), data=data)

    assert response.status_code == 401


@pytest.mark.django_db
def test_create_account_no_name(authenticated_client, test_user, test_wallets, test_account_types, test_account_institution_types, test_institution, test_currencies):

    data = {
        "type": test_account_types[0].name,
        "institution": test_institution[0].name,
        "currencies": [test_currencies[0].code],
        "wallets": [test_wallets[0].id],
        "description": "Checking account description",
        "owner": test_user[0].id,
        "co_owners": [test_user[1].id, test_user[2].id]
    }

    check_account_create_validation(authenticated_client,
                                    data=data,
                                    error_field='name',
                                    error_message='This field is required.',
                                    other_wallets=Account.objects.count())
    

@pytest.mark.django_db
def test_create_account_too_short_name(authenticated_client, test_user, test_wallets, test_account_types, test_account_institution_types, test_institution, test_currencies):
    
    data = {
        "name": "A",
        "type": test_account_types[0].name,
        "institution": test_institution[0].name,
        "currencies": [test_currencies[0].code],
        "wallets": [test_wallets[0].id],
        "description": "Checking account description",
        "owner": test_user[0].id,
        "co_owners": [test_user[1].id, test_user[2].id]
    }

    check_account_create_validation(authenticated_client,
                                    data=data,
                                    error_field='name',
                                    error_message='Name must be at least 3 characters long',
                                    other_wallets=Account.objects.count())
    

@pytest.mark.django_db
def test_create_account_too_long_name(authenticated_client, test_user, test_wallets, test_account_types, test_account_institution_types, test_institution, test_currencies):
        
    data = {
        "name": "A" * 101,
        "type": test_account_types[0].name,
        "institution": test_institution[0].name,
        "currencies": [test_currencies[0].code],
        "wallets": [test_wallets[0].id],
        "description": "Checking account description",
        "owner": test_user[0].id,
        "co_owners": [test_user[1].id, test_user[2].id]
    }

    check_account_create_validation(authenticated_client,
                                    data=data,
                                    error_field='name',
                                    error_message='Ensure this field has no more than 100 characters.',
                                    other_wallets=Account.objects.count())
    

@pytest.mark.django_db
def test_create_account_no_type(authenticated_client, test_user, test_wallets, test_account_types, test_account_institution_types, test_institution, test_currencies):
    
    data = {
        "name": "Checking Account",
        "institution": test_institution[0].name,
        "currencies": [test_currencies[0].code],
        "wallets": [test_wallets[0].id],
        "description": "Checking account description",
        "owner": test_user[0].id,
        "co_owners": [test_user[1].id, test_user[2].id]
    }

    check_account_create_validation(authenticated_client,
                                    data=data,
                                    error_field='type',
                                    error_message='This field is required.',
                                    other_wallets=Account.objects.count())
    

@pytest.mark.django_db
def test_create_account_type_empty_string(authenticated_client, test_user, test_wallets, test_account_types, test_account_institution_types, test_institution, test_currencies):
    
    data = {
        "name": "Checking Account",
        "type": "",
        "institution": test_institution[0].name,
        "currencies": [test_currencies[0].code],
        "wallets": [test_wallets[0].id],
        "description": "Checking account description",
        "owner": test_user[0].id,
        "co_owners": [test_user[1].id, test_user[2].id]
    }

    check_account_create_validation(authenticated_client,
                                    data=data,
                                    error_field='type',
                                    error_message='This field may not be null.',
                                    other_wallets=Account.objects.count())
    

@pytest.mark.django_db
def test_create_account_not_existing_type(authenticated_client, test_user, test_wallets, test_account_types, test_account_institution_types, test_institution, test_currencies):

    data = {
        "name": "Checking Account",
        "type": "Not Existing",
        "institution": test_institution[0].name,
        "currencies": [test_currencies[0].code],
        "wallets": [test_wallets[0].id],
        "description": "Checking account description",
        "owner": test_user[0].id,
        "co_owners": [test_user[1].id, test_user[2].id]
    }

    check_account_create_validation(authenticated_client,
                                    data=data,
                                    error_field='type',
                                    error_message='Not Existing is a wrong account type. Please provide a valid account type.',
                                    other_wallets=Account.objects.count())
    

@pytest.mark.django_db
def test_create_account_no_institution(authenticated_client, test_user, test_wallets, test_account_types, test_account_institution_types, test_institution, test_currencies):
    
    data = {
        "name": "Checking Account",
        "type": test_account_types[0].name,
        "currencies": [test_currencies[0].code],
        "wallets": [test_wallets[0].id],
        "description": "Checking account description",
        "owner": test_user[0].id,
        "co_owners": [test_user[1].id, test_user[2].id]
    }

    check_account_create_validation(authenticated_client,
                                    data=data,
                                    error_field='institution',
                                    error_message='This field is required.',
                                    other_wallets=Account.objects.count())
    

@pytest.mark.django_db
def test_create_account_institution_empty_string(authenticated_client, test_user, test_wallets, test_account_types, test_account_institution_types, test_institution, test_currencies):
    
    data = {
        "name": "Checking Account",
        "type": test_account_types[0].name,
        "institution": "",
        "currencies": [test_currencies[0].code],
        "wallets": [test_wallets[0].id],
        "description": "Checking account description",
        "owner": test_user[0].id,
        "co_owners": [test_user[1].id, test_user[2].id]
    }

    check_account_create_validation(authenticated_client,
                                    data=data,
                                    error_field='institution',
                                    error_message='This field may not be null.',
                                    other_wallets=Account.objects.count())
    

@pytest.mark.django_db
def test_create_account_not_existing_institution(authenticated_client, test_user, test_wallets, test_account_types, test_account_institution_types, test_institution, test_currencies):
    
    data = {
        "name": "Checking Account",
        "type": test_account_types[0].name,
        "institution": "Not Existing",
        "currencies": [test_currencies[0].code],
        "wallets": [test_wallets[0].id],
        "description": "Checking account description",
        "owner": test_user[0].id,
        "co_owners": [test_user[1].id, test_user[2].id]
    }

    check_account_create_validation(authenticated_client,
                                    data=data,
                                    error_field='institution',
                                    error_message='Not Existing is a wrong institution. Please provide a valid account institution.',
                                    other_wallets=Account.objects.count())
    

@pytest.mark.django_db
def test_create_account_no_currency(authenticated_client, test_user, test_wallets, test_account_types, test_account_institution_types, test_institution, test_currencies):
    
    data = {
        "name": "Checking Account",
        "type": test_account_types[0].name,
        "institution": test_institution[0].name,
        "wallets": [test_wallets[0].id],
        "description": "Checking account description",
        "owner": test_user[0].id,
        "co_owners": [test_user[1].id, test_user[2].id]
    }

    check_account_create_validation(authenticated_client,
                                    data=data,
                                    error_field='currencies',
                                    error_message='This field is required.',
                                    other_wallets=Account.objects.count())
    

@pytest.mark.django_db
def test_create_account_currency_empty_string(authenticated_client, test_user, test_wallets, test_account_types, test_account_institution_types, test_institution, test_currencies):
        
    data = {
        "name": "Checking Account",
        "type": test_account_types[0].name,
        "institution": test_institution[0].name,
        "currencies": "",
        "wallets": [test_wallets[0].id],
        "description": "Checking account description",
        "owner": test_user[0].id,
        "co_owners": [test_user[1].id, test_user[2].id]
    }

    check_account_create_validation(authenticated_client,
                                    data=data,
                                    error_field='currencies',
                                    error_message='Expected a list of items but got type "str".',
                                    other_wallets=Account.objects.count())

    
@pytest.mark.django_db
def test_create_account_not_existing_currency(authenticated_client, test_user, test_wallets, test_account_types, test_account_institution_types, test_institution, test_currencies):
    
    data = {
        "name": "Checking Account",
        "type": test_account_types[0].name,
        "institution": test_institution[0].name,
        "currencies": ["Not Existing"],
        "wallets": [test_wallets[0].id],
        "description": "Checking account description",
        "owner": test_user[0].id,
        "co_owners": [test_user[1].id, test_user[2].id]
    }

    check_account_create_validation(authenticated_client,
                                    data=data,
                                    error_field='currencies',
                                    error_message='Currency with short name Not Existing does not exist.',
                                    other_wallets=Account.objects.count())
    

@pytest.mark.django_db
def test_create_account_not_existing_wallet(authenticated_client, test_user, test_wallets, test_account_types, test_account_institution_types, test_institution, test_currencies):
        
    data = {
        "name": "Checking Account",
        "type": test_account_types[0].name,
        "institution": test_institution[0].name,
        "currencies": [test_currencies[0].code],
        "wallets": [100],
        "description": "Checking account description",
        "owner": test_user[0].id,
        "co_owners": [test_user[1].id, test_user[2].id]
    }

    check_account_create_validation(authenticated_client,
                                    data=data,
                                    error_field='wallets',
                                    error_message='Invalid pk "100" - object does not exist.',
                                    other_wallets=Account.objects.count())
    
@pytest.mark.django_db
def test_create_account_add_wallet_not_owned(authenticated_client, test_user, test_wallets, test_account_types, test_account_institution_types, test_institution, test_currencies):
    
    #Prepare data
    test_wallets[1].owner = test_user[1]
    test_wallets[1].co_owners.clear()
    test_wallets[1].save()

    data = {
        "name": "Checking Account",
        "type": test_account_types[0].name,
        "institution": test_institution[0].name,
        "currencies": [test_currencies[0].code],
        "wallets": [test_wallets[1].id],
        "description": "Checking account description",
        "owner": test_user[0].id,
        "co_owners": [test_user[1].id, test_user[2].id]
    }

    check_account_create_validation(authenticated_client,
                                    data=data,
                                    error_field='wallets',
                                    error_message='You do not have permission to create an account for this wallet.',
                                    other_wallets=Account.objects.count())  

@pytest.mark.django_db
def test_create_account_too_long_description(authenticated_client, test_user, test_wallets, test_account_types, test_account_institution_types, test_institution, test_currencies):
        
    data = {
        "name": "Checking Account",
        "type": test_account_types[0].name,
        "institution": test_institution[0].name,
        "currencies": [test_currencies[0].code],
        "wallets": [test_wallets[0].id],
        "description": "A" * 1001,
        "owner": test_user[0].id,
        "co_owners": [test_user[1].id, test_user[2].id]
    }

    check_account_create_validation(authenticated_client,
                                    data=data,
                                    error_field='description',
                                    error_message='Ensure this field has no more than 1000 characters.',
                                    other_wallets=Account.objects.count())
        
@pytest.mark.django_db
def test_create_account_not_existing_co_owner(authenticated_client, test_user, test_wallets, test_account_types, test_account_institution_types, test_institution, test_currencies):
        
    data = {
        "name": "Checking Account",
        "type": test_account_types[0].name,
        "institution": test_institution[0].name,
        "currencies": [test_currencies[0].code],
        "wallets": [test_wallets[0].id],
        "description": "Checking account description",
        "owner": test_user[0].id,
        "co_owners": [100]
    }

    check_account_create_validation(authenticated_client,
                                    data=data,
                                    error_field='co_owners',
                                    error_message='Invalid pk "100" - object does not exist.',
                                    other_wallets=Account.objects.count())
    
@pytest.mark.django_db
def test_create_account_owner_as_co_owner(authenticated_client, test_user, test_wallets, test_account_types, test_account_institution_types, test_institution, test_currencies):
        
    data = {
        "name": "Checking Account",
        "type": test_account_types[0].name,
        "institution": test_institution[0].name,
        "currencies": [test_currencies[0].code],
        "wallets": [test_wallets[0].id],
        "description": "Checking account description",
        "owner": test_user[0].id,
        "co_owners": [test_user[0].id]
    }

    check_account_create_validation(authenticated_client,
                                    data=data,
                                    error_field='co_owners',
                                    error_message='Owner cannot be a co-owner of the wallet.',
                                    other_wallets=Account.objects.count())

@pytest.mark.django_db
def test_create_duplicated_name(authenticated_client, test_user, test_wallets, test_account_types, test_account_institution_types, test_institution, test_currencies, test_accounts):

    existing_user_account = Account.objects.filter(owner=test_user[0]).first()

    data = {
        "name": existing_user_account.name,
        "type": test_account_types[0].name,
        "institution": test_institution[0].name,
        "currencies": [test_currencies[0].code],
        "wallets": [test_wallets[0].id],
        "description": "Checking account description",
        "owner": test_user[0].id,
        "co_owners": [test_user[1].id, test_user[2].id]
    }

    check_account_create_validation(authenticated_client,
                                    data=data,
                                    error_field='name',
                                    error_message='Account with this Owner and Name already exists.',
                                    other_wallets=Account.objects.count())
    
@pytest.mark.django_db
def test_update_account_by_owner(api_client, test_user, test_accounts, test_wallets, test_account_types, test_account_institution_types, test_institution, test_currencies):
        
    account_to_update = test_accounts[0]

    #Prepare data
    test_wallets[1].owner = account_to_update.owner
    test_wallets[1].co_owners.clear()
    test_wallets[1].save()

    api_client.force_authenticate(user=account_to_update.owner)

    data = {
        "name": "Updated Account",
        "type": test_account_types[1].name,
        "institution": test_institution[1].name,
        "currencies": [test_currencies[1].code, test_currencies[2].code],
        "wallets": [test_wallets[1].id],
        "description": "Updated account description",
        "co_owners": [test_user[2].id, test_user[3].id]
    }

    response = api_client.put(api_url(f'accounts/{account_to_update.id}/'), data=data)  

    assert response.status_code == 200
    assert response.data['name'] == data['name']
    assert response.data['description'] == data['description']
    assert response.data['owner_id'] == account_to_update.owner.id
    assert response.data['wallets'] == data['wallets']
    assert response.data['type'] == test_account_types[1].name
    assert response.data['institution'] == test_institution[1].name
    assert response.data['currencies'] == [currency.code for currency in account_to_update.currencies.all()]


@pytest.mark.django_db
def test_update_account_by_co_owner(api_client, test_user, test_accounts, test_wallets, test_account_types, test_account_institution_types, test_institution, test_currencies):
        
    account_to_update = test_accounts[0]

    #Prepare data
    account_to_update.co_owners.clear()
    account_to_update.co_owners.add(test_user[1])
    account_to_update.save()

    test_wallets[1].owner = test_user[1]
    test_wallets[1].co_owners.clear()
    test_wallets[1].save()

    api_client.force_authenticate(user=account_to_update.co_owners.all()[0])

    data = {
        "name": "Updated Account",
        "type": test_account_types[1].name,
        "institution": test_institution[1].name,
        "currencies": [test_currencies[1].code],
        "wallets": [test_wallets[1].id],
        "description": "Updated account description",
        "co_owners": [test_user[2].id, test_user[3].id]
    }

    response = api_client.put(api_url(f'accounts/{account_to_update.id}/'), data=data)

    assert response.status_code == 200
    assert response.data['name'] == data['name']
    assert response.data['description'] == data['description']
    assert response.data['owner_id'] == account_to_update.owner.id
    assert response.data['wallets'] == data['wallets']
    assert response.data['type'] == test_account_types[1].name
    assert response.data['institution'] == test_institution[1].name
    assert response.data['currencies'] == [currency.code for currency in account_to_update.currencies.all()]


@pytest.mark.django_db
def test_update_account_to_other_institution(authenticated_client, test_user, test_accounts, test_wallets, test_account_types, test_account_institution_types, test_institution, test_currencies):
        
    account_to_update = test_accounts[0]

    #Prepare data
    test_wallets[1].owner = account_to_update.owner
    test_wallets[1].co_owners.clear()
    test_wallets[1].save()


    authenticated_client.force_authenticate(user=account_to_update.owner)

    data = {
        "name": "Updated Account",
        "type": test_account_types[1].name,
        "institution": "Other",
        "other_institution": "Other Institution",
        "currencies": [test_currencies[1].code],
        "wallets": [test_wallets[1].id],
        "description": "Updated account description",
        "co_owners": [test_user[2].id, test_user[3].id]
    }

    response = authenticated_client.put(api_url(f'accounts/{account_to_update.id}/'), data=data)

    assert response.status_code == 200
    assert response.data['name'] == data['name']
    assert response.data['description'] == data['description']
    assert response.data['owner_id'] == account_to_update.owner.id
    assert response.data['wallets'] == data['wallets']
    assert response.data['type'] == test_account_types[1].name
    assert response.data['institution'] == "Other"
    assert response.data['other_institution'] == data['other_institution']
    assert response.data['currencies'] == [currency.code for currency in account_to_update.currencies.all()]


@pytest.mark.django_db
def test_update_account_by_co_owner(api_client, test_user, test_accounts, test_wallets, test_account_types, test_account_institution_types, test_institution, test_currencies):

    account_to_update = test_accounts[0]

    #Prepare data
    account_to_update.co_owners.clear()
    account_to_update.co_owners.add(test_user[1])
    account_to_update.save()

    test_wallets[1].owner = test_user[1]
    test_wallets[1].co_owners.clear()
    test_wallets[1].save()

    api_client.force_authenticate(user=account_to_update.co_owners.all()[0])

    data = {
        "name": "Updated Account",
        "type": test_account_types[1].name,
        "institution": test_institution[1].name,
        "currencies": [test_currencies[1].code],
        "wallets": [test_wallets[1].id],
        "description": "Updated account description",
        "co_owners": [test_user[2].id, test_user[3].id]
    }

    response = api_client.put(api_url(f'accounts/{account_to_update.id}/'), data=data)

    assert response.status_code == 200
    assert response.data['name'] == data['name']
    assert response.data['description'] == data['description']
    assert response.data['owner_id'] == account_to_update.owner.id
    assert response.data['wallets'] == data['wallets']
    assert response.data['type'] == test_account_types[1].name
    assert response.data['institution'] == test_institution[1].name
    assert response.data['currencies'] == [currency.code for currency in account_to_update.currencies.all()]


@pytest.mark.django_db
def test_update_account_leave_old_name(authenticated_client, test_user, test_accounts, test_wallets, test_account_types, test_account_institution_types, test_institution, test_currencies):
            
    account_to_update = test_accounts[0]

    #Prepare data
    test_wallets[1].owner = account_to_update.owner
    test_wallets[1].co_owners.clear()
    test_wallets[1].save()
    
    authenticated_client.force_authenticate(user=account_to_update.owner)

    data = {
        "name": account_to_update.name,
        "type": test_account_types[1].name,
        "institution": test_institution[1].name,
        "currencies": [test_currencies[1].code],
        "wallets": [test_wallets[1].id],
        "description": "Updated account description",
        "co_owners": [test_user[2].id, test_user[3].id]
    }

    response = authenticated_client.put(api_url(f'accounts/{account_to_update.id}/'), data=data)

    assert response.status_code == 200
    assert response.data['name'] == data['name']
    assert response.data['description'] == data['description']
    assert response.data['owner_id'] == account_to_update.owner.id
    assert response.data['wallets'] == data['wallets']
    assert response.data['type'] == test_account_types[1].name
    assert response.data['institution'] == test_institution[1].name
    assert response.data['currencies'] == [currency.code for currency in account_to_update.currencies.all()]


@pytest.mark.django_db
def test_update_account_no_auth(api_client, test_user, test_accounts, test_wallets, test_account_types, test_account_institution_types, test_institution, test_currencies):
        
    account_to_update = test_accounts[0]

    data = {
        "name": "Updated Account",
        "type": test_account_types[1].name,
        "institution": test_institution[1].name,
        "currencies": [test_currencies[1].code],
        "wallets": [test_wallets[1].id],
        "description": "Updated account description",
        "co_owners": [test_user[2].id, test_user[3].id]
    }

    response = api_client.put(api_url(f'accounts/{account_to_update.id}/'), data=data)

    assert response.status_code == 401
    assert response.data.get('detail') == 'Authentication credentials were not provided.'


@pytest.mark.django_db
def test_update_account_by_nor_owner_or_co_owner(api_client, test_user, test_accounts, test_wallets, test_account_types, test_account_institution_types, test_institution, test_currencies):

    account_to_update = test_accounts[0]

    #Prepare data
    account_to_update.co_owners.clear()
    account_to_update.owner = test_user[1]
    account_to_update.save()

    for user in test_user:
        if user != account_to_update.owner:
            api_client.force_authenticate(user=user)
            break

    data = {
        "name": "Updated Account",
        "type": test_account_types[1].name,
        "institution": test_institution[1].name,
        "currencies": [test_currencies[1].code],
        "wallets": [test_wallets[1].id],
        "description": "Updated account description",
        "co_owners": [test_user[2].id, test_user[3].id]
    }

    response = api_client.put(api_url(f'accounts/{account_to_update.id}/'), data=data)

    assert response.status_code == 403
    assert response.data.get('detail') == 'You do not have permission to perform this action.'

@pytest.mark.django_db
def test_update_account_not_found(api_client):
        
    response = api_client.put(api_url(f'accounts/100/'))

    assert response.status_code == 404
    assert response.data.get('detail') == 'No Account matches the given query.'


@pytest.mark.django_db
def test_update_account_to_other_institution_no_other(authenticated_client, test_user, test_accounts, test_wallets, test_account_types, test_account_institution_types, test_institution, test_currencies):
            
    account_to_update = test_accounts[0]

    #Prepare data
    test_wallets[1].owner = account_to_update.owner
    test_wallets[1].co_owners.clear()
    test_wallets[1].save()

    authenticated_client.force_authenticate(user=account_to_update.owner)

    data = {
        "name": "Updated Account",
        "type": test_account_types[1].name,
        "institution": "Other",
        "currencies": [test_currencies[1].code],
        "wallets": [test_wallets[1].id],
        "description": "Updated account description",
        "owner": account_to_update.owner.id,
        "co_owners": [test_user[2].id, test_user[3].id],
        "id" : account_to_update.id
    }

    check_account_update_validation(authenticated_client,
                                    data=data,
                                    error_field='other_institution',
                                    error_message='This field cannot be empty if institution is set to "Other".',
                                    other_wallets=Account.objects.count())
    

@pytest.mark.django_db
def test_update_account_institution_selected_and_other(authenticated_client, test_user, test_accounts, test_wallets, test_account_types, test_account_institution_types, test_institution, test_currencies):

    account_to_update = test_accounts[0]
    #Prepare data
    test_wallets[1].owner = account_to_update.owner
    test_wallets[1].co_owners.clear()
    test_wallets[1].save()

    authenticated_client.force_authenticate(user=account_to_update.owner)

    data = {
        "name": "Updated Account",
        "type": test_account_types[1].name,
        "institution": test_institution[1].name,
        "other_institution": "Other Institution",
        "currencies": [test_currencies[1].code],
        "wallets": [test_wallets[1].id],
        "description": "Updated account description",
        "co_owners": [test_user[2].id, test_user[3].id],
        "owner": account_to_update.owner.id,
        "id" : account_to_update.id
    }

    check_account_update_validation(authenticated_client,
                                    data=data,
                                    error_field='other_institution',
                                    error_message="This field must be empty if institution is not set to 'Other'.",
                                    other_wallets=Account.objects.count())

@pytest.mark.django_db
def test_update_account_no_name(authenticated_client, test_user, test_accounts, test_wallets, test_account_types, test_account_institution_types, test_institution, test_currencies):
        
    account_to_update = test_accounts[0]
    authenticated_client.force_authenticate(user=account_to_update.owner)

    data = {
        "type": test_account_types[1].name,
        "institution": test_institution[1].name,
        "currencies": [test_currencies[1].code],
        "wallets": [test_wallets[1].id],
        "description": "Updated account description",
        "co_owners": [test_user[2].id, test_user[3].id],
        "owner": test_user[0].id,
        "id" : account_to_update.id
    }

    check_account_update_validation(authenticated_client,
                                    data=data,
                                    error_field='name',
                                    error_message='This field is required.',
                                    other_wallets=Account.objects.count())
    

@pytest.mark.django_db
def test_update_account_too_short_name(authenticated_client, test_user, test_accounts, test_wallets, test_account_types, test_account_institution_types, test_institution, test_currencies):
        
    account_to_update = test_accounts[0]
    #Prepare data
    test_wallets[1].owner = account_to_update.owner
    test_wallets[1].co_owners.clear()
    test_wallets[1].save()

    authenticated_client.force_authenticate(user=account_to_update.owner)

    data = {
        "name": "A",
        "type": test_account_types[1].name,
        "institution": test_institution[1].name,
        "currencies": [test_currencies[1].code],
        "wallets": [test_wallets[1].id],
        "description": "Updated account description",
        "co_owners": [test_user[2].id, test_user[3].id],
        "owner": test_user[0].id,
        "id" : account_to_update.id
    }

    check_account_update_validation(authenticated_client,
                                    data=data,
                                    error_field='name',
                                    error_message='Name must be at least 3 characters long',
                                    other_wallets=Account.objects.count())


@pytest.mark.django_db
def test_update_account_too_long_name(authenticated_client, test_user, test_accounts, test_wallets, test_account_types, test_account_institution_types, test_institution, test_currencies):
        
    account_to_update = test_accounts[0]
    #Prepare data
    test_wallets[1].owner = account_to_update.owner
    test_wallets[1].co_owners.clear()
    test_wallets[1].save()

    authenticated_client.force_authenticate(user=account_to_update.owner)

    data = {
        "name": "A" * 101,
        "type": test_account_types[1].name,
        "institution": test_institution[1].name,
        "currencies": [test_currencies[1].code],
        "wallets": [test_wallets[1].id],
        "description": "Updated account description",
        "co_owners": [test_user[2].id, test_user[3].id],
        "owner": test_user[0].id,
        "id" : account_to_update.id
    }

    check_account_update_validation(authenticated_client,
                                    data=data,
                                    error_field='name',
                                    error_message='Ensure this field has no more than 100 characters.',
                                    other_wallets=Account.objects.count())
    
@pytest.mark.django_db
def test_update_account_no_type(authenticated_client, test_user, test_accounts, test_wallets, test_account_types, test_account_institution_types, test_institution, test_currencies):
        
    account_to_update = test_accounts[0]
    authenticated_client.force_authenticate(user=account_to_update.owner)

    data = {
        "name": "Updated Account",
        "institution": test_institution[1].name,
        "currencies": [test_currencies[1].code],
        "wallets": [test_wallets[1].id],
        "description": "Updated account description",
        "co_owners": [test_user[2].id, test_user[3].id],
        "owner": test_user[0].id,
        "id" : account_to_update.id
    }

    check_account_update_validation(authenticated_client,
                                    data=data,
                                    error_field='type',
                                    error_message='This field is required.',
                                    other_wallets=Account.objects.count())
    
@pytest.mark.django_db
def test_update_account_type_empty_string(authenticated_client, test_user, test_accounts, test_wallets, test_account_types, test_account_institution_types, test_institution, test_currencies):
            
    account_to_update = test_accounts[0]
    #Prepare data
    test_wallets[1].owner = account_to_update.owner
    test_wallets[1].co_owners.clear()
    test_wallets[1].save()
    authenticated_client.force_authenticate(user=account_to_update.owner)

    data = {
        "name": "Updated Account",
        "type": "",
        "institution": test_institution[1].name,
        "currencies":[ test_currencies[1].code],
        "wallets": [test_wallets[1].id],
        "description": "Updated account description",
        "co_owners": [test_user[2].id, test_user[3].id],
        "owner": test_user[0].id,
        "id" : account_to_update.id
    }

    check_account_update_validation(authenticated_client,
                                    data=data,
                                    error_field='type',
                                    error_message='This field may not be null.',
                                    other_wallets=Account.objects.count())


@pytest.mark.django_db
def test_update_account_not_existing_type(authenticated_client, test_user, test_accounts, test_wallets, test_account_types, test_account_institution_types, test_institution, test_currencies):
        
    account_to_update = test_accounts[0]
    authenticated_client.force_authenticate(user=account_to_update.owner)

    data = {
        "name": "Updated Account",
        "type": "Not Existing",
        "institution": test_institution[1].name,
        "currencies": [test_currencies[1].code],
        "wallets": [test_wallets[1].id],
        "description": "Updated account description",
        "co_owners": [test_user[2].id, test_user[3].id],
        "owner": test_user[0].id,
        "id" : account_to_update.id
    }

    check_account_update_validation(authenticated_client,
                                    data=data,
                                    error_field='type',
                                    error_message='Not Existing is a wrong account type. Please provide a valid account type.',
                                    other_wallets=Account.objects.count())
    

@pytest.mark.django_db
def test_update_account_no_institution(authenticated_client, test_user, test_accounts, test_wallets, test_account_types, test_account_institution_types, test_institution, test_currencies):
        
    account_to_update = test_accounts[0]

    #Prepare data
    test_wallets[1].owner = account_to_update.owner
    test_wallets[1].co_owners.clear()
    test_wallets[1].save()

    authenticated_client.force_authenticate(user=account_to_update.owner)

    data = {
        "name": "Updated Account",
        "type": test_account_types[1].name,
        "currencies": [test_currencies[1].code],
        "wallets": [test_wallets[1].id],
        "description": "Updated account description",
        "co_owners": [test_user[2].id, test_user[3].id],
        "owner": test_user[0].id,
        "id" : account_to_update.id
    }

    check_account_update_validation(authenticated_client,
                                    data=data,
                                    error_field='institution',
                                    error_message='This field is required.',
                                    other_wallets=Account.objects.count())
    

@pytest.mark.django_db
def test_update_account_institution_empty_string(authenticated_client, test_user, test_accounts, test_wallets, test_account_types, test_account_institution_types, test_institution, test_currencies):
            
    account_to_update = test_accounts[0]
    #Prepare data
    test_wallets[1].owner = account_to_update.owner
    test_wallets[1].co_owners.clear()
    test_wallets[1].save()
    authenticated_client.force_authenticate(user=account_to_update.owner)

    data = {
        "name": "Updated Account",
        "type": test_account_types[1].name,
        "institution": "",
        "currencies": [test_currencies[1].code],
        "wallets": [test_wallets[1].id],
        "description": "Updated account description",
        "co_owners": [test_user[2].id, test_user[3].id],
        "owner": test_user[0].id,
        "id" : account_to_update.id
    }

    check_account_update_validation(authenticated_client,
                                    data=data,
                                    error_field='institution',
                                    error_message='This field may not be null.',
                                    other_wallets=Account.objects.count())
    
@pytest.mark.django_db
def test_update_account_not_existing_institution(authenticated_client, test_user, test_accounts, test_wallets, test_account_types, test_account_institution_types, test_institution, test_currencies):
        
    account_to_update = test_accounts[0]
    #Prepare data
    test_wallets[1].owner = account_to_update.owner
    test_wallets[1].co_owners.clear()
    test_wallets[1].save()
    authenticated_client.force_authenticate(user=account_to_update.owner)

    data = {
        "name": "Updated Account",
        "type": test_account_types[1].name,
        "institution": "Not Existing",
        "currencies": [test_currencies[1].code],
        "wallets": [test_wallets[1].id],
        "description": "Updated account description",
        "co_owners": [test_user[2].id, test_user[3].id],
        "owner": test_user[0].id,
        "id" : account_to_update.id
    }

    check_account_update_validation(authenticated_client,
                                    data=data,
                                    error_field='institution',
                                    error_message='Not Existing is a wrong institution. Please provide a valid account institution.',
                                    other_wallets=Account.objects.count())
    

@pytest.mark.django_db
def test_update_account_no_currency(authenticated_client, test_user, test_accounts, test_wallets, test_account_types, test_account_institution_types, test_institution, test_currencies):
        
    account_to_update = test_accounts[0]
    #Prepare data
    test_wallets[1].owner = account_to_update.owner
    test_wallets[1].co_owners.clear()
    test_wallets[1].save()
    authenticated_client.force_authenticate(user=account_to_update.owner)

    data = {
        "name": "Updated Account",
        "type": test_account_types[1].name,
        "institution": test_institution[1].name,
        "wallets": [test_wallets[1].id],
        "description": "Updated account description",
        "co_owners": [test_user[2].id, test_user[3].id],
        "owner": test_user[0].id,
        "id" : account_to_update.id
    }

    check_account_update_validation(authenticated_client,
                                    data=data,
                                    error_field='currencies',
                                    error_message='This field is required.',
                                    other_wallets=Account.objects.count())
    
@pytest.mark.django_db
def test_update_account_currency_empty_string(authenticated_client, test_user, test_accounts, test_wallets, test_account_types, test_account_institution_types, test_institution, test_currencies):
                
    account_to_update = test_accounts[0]
    #Prepare data
    test_wallets[1].owner = account_to_update.owner
    test_wallets[1].co_owners.clear()
    test_wallets[1].save()
    authenticated_client.force_authenticate(user=account_to_update.owner)

    data = {
        "name": "Updated Account",
        "type": test_account_types[1].name,
        "institution": test_institution[1].name,
        "currencies": "",
        "wallets": [test_wallets[1].id],
        "description": "Updated account description",
        "co_owners": [test_user[2].id, test_user[3].id],
        "owner": test_user[0].id,
        "id" : account_to_update.id
    }

    check_account_update_validation(authenticated_client,
                                    data=data,
                                    error_field='currencies',
                                    error_message='Expected a list of items but got type "str".',
                                    other_wallets=Account.objects.count())
    
@pytest.mark.django_db
def test_update_account_not_existing_currency(authenticated_client, test_user, test_accounts, test_wallets, test_account_types, test_account_institution_types, test_institution, test_currencies):
        
    account_to_update = test_accounts[0]
    #Prepare data
    test_wallets[1].owner = account_to_update.owner
    test_wallets[1].co_owners.clear()
    test_wallets[1].save()
    authenticated_client.force_authenticate(user=account_to_update.owner)

    data = {
        "name": "Updated Account",
        "type": test_account_types[1].name,
        "institution": test_institution[1].name,
        "currencies": ["Not Existing"],
        "wallets": [test_wallets[1].id],
        "description": "Updated account description",
        "co_owners": [test_user[2].id, test_user[3].id],
        "owner": test_user[0].id,
        "id" : account_to_update.id
    }

    check_account_update_validation(authenticated_client,
                                    data=data,
                                    error_field='currencies',
                                    error_message='Currency with short name Not Existing does not exist.',
                                    other_wallets=Account.objects.count())
    

@pytest.mark.django_db
def test_update_account_not_existing_wallet(authenticated_client, test_user, test_accounts, test_wallets, test_account_types, test_account_institution_types, test_institution, test_currencies):
        
    account_to_update = test_accounts[0]
    authenticated_client.force_authenticate(user=account_to_update.owner)

    data = {
        "name": "Updated Account",
        "type": test_account_types[1].name,
        "institution": test_institution[1].name,
        "currencies": [test_currencies[1].code],
        "wallets": [100],
        "description": "Updated account description",
        "co_owners": [test_user[2].id, test_user[3].id],
        "owner": test_user[0].id,
        "id" : account_to_update.id
    }

    check_account_update_validation(authenticated_client,
                                    data=data,
                                    error_field='wallets',
                                    error_message='Invalid pk "100" - object does not exist.',
                                    other_wallets=Account.objects.count())
    

    
@pytest.mark.django_db
def test_update_account_too_long_description(authenticated_client, test_user, test_accounts, test_wallets, test_account_types, test_account_institution_types, test_institution, test_currencies):
        
    account_to_update = test_accounts[0]
    authenticated_client.force_authenticate(user=account_to_update.owner)

    data = {
        "name": "Updated Account",
        "type": test_account_types[1].name,
        "institution": test_institution[1].name,
        "currencies": [test_currencies[1].code],
        "wallets": [test_wallets[1].id],
        "description": "A" * 1001,
        "co_owners": [test_user[2].id, test_user[3].id],
        "owner": test_user[0].id,
        "id" : account_to_update.id
    }

    check_account_update_validation(authenticated_client,
                                    data=data,
                                    error_field='description',
                                    error_message='Ensure this field has no more than 1000 characters.',
                                    other_wallets=Account.objects.count())
    

@pytest.mark.django_db
def test_update_account_not_existing_co_owner(authenticated_client, test_user, test_accounts, test_wallets, test_account_types, test_account_institution_types, test_institution, test_currencies):
        
    account_to_update = test_accounts[0]
    authenticated_client.force_authenticate(user=account_to_update.owner)

    data = {
        "name": "Updated Account",
        "type": test_account_types[1].name,
        "institution": test_institution[1].name,
        "currencies": [test_currencies[1].code],
        "wallets": [test_wallets[1].id],
        "description": "Updated account description",
        "co_owners": [100],
        "owner": test_user[0].id,
        "id" : account_to_update.id
    }

    check_account_update_validation(authenticated_client,
                                    data=data,
                                    error_field='co_owners',
                                    error_message='Invalid pk "100" - object does not exist.',
                                    other_wallets=Account.objects.count())
    

@pytest.mark.django_db
def test_update_account_owner_as_co_owner(authenticated_client, test_user, test_accounts, test_wallets, test_account_types, test_account_institution_types, test_institution, test_currencies):
        
    account_to_update = test_accounts[0]
    authenticated_client.force_authenticate(user=account_to_update.owner)

    data = {
        "name": "Updated Account",
        "type": test_account_types[1].name,
        "institution": test_institution[1].name,
        "currencies": [test_currencies[1].code],
        "wallets": [test_wallets[1].id],
        "description": "Updated account description",
        "co_owners": [test_user[0].id],
        "owner": test_user[0].id,
        "id" : account_to_update.id
    }

    check_account_update_validation(authenticated_client,
                                    data=data,
                                    error_field='co_owners',
                                    error_message='Owner cannot be a co-owner of the wallet.',
                                    other_wallets=Account.objects.count())
    

@pytest.mark.django_db
def test_update_duplicated_name(authenticated_client, test_user, test_accounts, test_wallets, test_account_types, test_account_institution_types, test_institution, test_currencies):
        
    first_account = test_accounts[0]
    second_account = test_accounts[1]

    first_account.owner = test_user[0]
    first_account.save()

    second_account.owner = test_user[0]
    second_account.save()

    authenticated_client.force_authenticate(user=first_account.owner)

    data = {
        "name": second_account.name,
        "type": test_account_types[1].name,
        "institution": test_institution[1].name,
        "currencies": [test_currencies[1].code],
        "wallets": [test_wallets[1].id],
        "description": "Updated account description",
        "co_owners": [test_user[2].id, test_user[3].id],
        "owner": test_user[0].id,
        "id" : first_account.id
    }


    check_account_update_validation(authenticated_client,
                                    data=data,
                                    error_field='name',
                                    error_message='Account with this Owner and Name already exists.',
                                    other_wallets=Account.objects.count())
    

@pytest.mark.django_db
def test_delete_account_by_owner(api_client, test_user, test_accounts):
            
        account_to_delete = test_accounts[0]
        api_client.force_authenticate(user=account_to_delete.owner)
    
        response = api_client.delete(api_url(f'accounts/{account_to_delete.id}/'))
    
        assert response.status_code == 204
        assert Account.objects.count() == len(test_accounts) - 1

        response = api_client.get(api_url(f'accounts/{account_to_delete.id}/'))

        assert response.status_code == 404


@pytest.mark.django_db
def test_delete_account_by_co_owner(api_client, test_user, test_accounts):
            
        account_to_delete = test_accounts[0]
        api_client.force_authenticate(user=account_to_delete.co_owners.all()[0])
    
        response = api_client.delete(api_url(f'accounts/{account_to_delete.id}/'))
    
        assert response.status_code == 403
        assert response.data.get('detail') is not None
        assert response.data['detail'] == 'You do not have permission to perform this action.'
    
        # Make a GET request to the /wallets/1/ endpoint
        api_client.force_authenticate(user = account_to_delete.owner)
        response = api_client.get(api_url(f'wallets/{account_to_delete.id}/'))
        
        assert response.status_code == 200


@pytest.mark.django_db
def test_delete_account_no_auth(api_client, test_user, test_accounts):
            
    account_to_delete = test_accounts[0]

    response = api_client.delete(api_url(f'accounts/{account_to_delete.id}/'))

    assert response.status_code == 401
    assert Account.objects.count() == len(test_accounts)


@pytest.mark.django_db
def test_delete_account_by_nor_owner_or_co_owner(api_client, test_user, test_accounts):
            
    account_to_delete = test_accounts[0]
    api_client.force_authenticate(user=test_user[3])

    response = api_client.delete(api_url(f'accounts/{account_to_delete.id}/'))

    assert response.status_code == 403
    assert response.data.get('detail') is not None
    assert response.data['detail'] == 'You do not have permission to perform this action.'
    assert Account.objects.count() == len(test_accounts)


@pytest.mark.django_db
def test_delete_account_not_found(api_client):
            
    response = api_client.delete(api_url(f'accounts/100/'))

    assert response.status_code == 404
    assert response.data.get('detail') == 'No Account matches the given query.'



def check_account_create_validation(api_client, data, error_field, error_message, other_wallets = 0):
    

    user_to_log = User.objects.get(id=data['owner'])
    api_client.force_authenticate(user_to_log)

    data = data.copy()
    data.pop('owner')


    response = api_client.post(api_url('accounts/'), data = data, format='json')

    assert response.status_code == 400
    assert response.data.get(error_field) is not None
    assert str(response.data.get(error_field)[0]) == error_message

    assert Account.objects.count() == other_wallets


def check_account_update_validation(api_client, data, error_field, error_message, other_wallets = 0):
    
    user_to_log = User.objects.get(id=data['owner'])
    api_client.force_authenticate(user_to_log)

    data = data.copy()
    data.pop('owner')
    id_to_send=data.pop('id')

    response = api_client.put(api_url(f'accounts/{id_to_send}/'), data = data, format='json')

    assert response.status_code == 400

    assert response.data.get(error_field) is not None
    assert str(response.data.get(error_field)[0]) == error_message

    assert Account.objects.count() == other_wallets

