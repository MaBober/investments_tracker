import pytest
from pprint import pprint

from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APIClient

from wallets.tests.wallet.test_fixture import test_user, authenticated_client, api_client, api_url, test_wallets
from wallets.models import Wallet



@pytest.mark.django_db
def test_get_wallets(authenticated_client, test_user, test_wallets):

    # Make a GET request to the /wallets/ endpoint
    response = authenticated_client.get(api_url('wallets/'))

    assert response.status_code == 200
    assert response.data['count'] == len(test_wallets)
    assert response.data['results'][0]['owner_id'] == str(test_wallets[0].owner.id)
    assert response.data['results'][0]['name'] == test_wallets[0].name
    assert response.data['results'][0]['description'] == test_wallets[0].description
    assert response.data['results'][0]['co_owners'] == list(test_wallets[0].co_owners.all())
    assert response.data['results'][0]['created_at'] == test_wallets[0].created_at.astimezone(timezone.get_current_timezone()).isoformat()
    assert response.data['results'][0]['updated_at'] == test_wallets[0].updated_at.astimezone(timezone.get_current_timezone()).isoformat()

    assert response.data['results'][1]['co_owners'] == list(test_wallets[1].co_owners.all())

@pytest.mark.django_db
def test_get_wallets_no_auth(api_client, test_user, test_wallets):
    
    # Make a GET request to the /wallets/ endpoint
    response = api_client.get(api_url('wallets/'))
    
    assert response.status_code == 401

@pytest.mark.django_db
def test_get_single_wallet(authenticated_client, test_user, test_wallets):

    # Make a GET request to the /wallets/1/ endpoint
    wallet_to_test = test_wallets[1]

    response = authenticated_client.get(api_url(f'wallets/{wallet_to_test.id}/'))

    assert response.status_code == 200
    assert response.data['owner_id'] == str(wallet_to_test.owner.id)
    assert response.data['name'] == wallet_to_test.name
    assert response.data['description'] == wallet_to_test.description
    assert response.data['co_owners'] == list(wallet_to_test.co_owners.all())
    assert response.data['created_at'] == wallet_to_test.created_at.astimezone(timezone.get_current_timezone()).isoformat()
    assert response.data['updated_at'] == wallet_to_test.updated_at.astimezone(timezone.get_current_timezone()).isoformat()
    
@pytest.mark.django_db
def test_get_single_wallet_no_auth(api_client, test_user, test_wallets):
        
    # Make a GET request to the /wallets/1/ endpoint
    wallet_to_test = test_wallets[1]

    response = api_client.get(api_url(f'wallets/{wallet_to_test.id}/'))

    assert response.status_code == 401

@pytest.mark.django_db
def test_get_single_wallet_not_found(authenticated_client, test_user, test_wallets):
    
    # Make a GET request to the /wallets/100/ endpoint
    response = authenticated_client.get(api_url('wallets/100/'))

    assert response.status_code == 404

@pytest.mark.django_db
def test_create_wallet_single_owner(authenticated_client, test_user):
        
    # Make a POST request to the /wallets/ endpoint
    new_wallet_data = {
        'name': 'New Wallet',
        'description': 'New Wallet description'
    }

    response = authenticated_client.post(api_url('wallets/'), new_wallet_data, format='json')

    assert response.status_code == 201
    assert response.data['owner_id'] == test_user[0].id
    assert response.data['name'] == new_wallet_data['name']
    assert response.data['description'] == new_wallet_data['description']
    assert response.data['co_owners'] == []

    wallet_id = response.data['id']

    # Make a GET request to the /wallets/ endpoint
    response = authenticated_client.get(api_url(f'wallets/{wallet_id}/'))

    assert response.status_code == 200
    assert response.data['owner_id'] == str(test_user[0].id)
    assert response.data['name'] == new_wallet_data['name']
    assert response.data['description'] == new_wallet_data['description']
    assert response.data['co_owners'] == []
    assert timezone.now() - timezone.datetime.fromisoformat(response.data['created_at']) < timezone.timedelta(seconds=1)

@pytest.mark.django_db
def test_create_wallet_multiple_owners(authenticated_client, test_user):
        
        # Make a POST request to the /wallets/ endpoint
        new_wallet_data = {
            'name': 'New Wallet',
            'description': 'New Wallet description',
            'co_owners': [test_user[1].id]
        }
    
        response = authenticated_client.post(api_url('wallets/'), new_wallet_data, format='json')
    
        assert response.status_code == 201
        assert response.data['owner_id'] == test_user[0].id
        assert response.data['name'] == new_wallet_data['name']
        assert response.data['description'] == new_wallet_data['description']
        assert response.data['co_owners'] == [test_user[1].id]
    
        wallet_id = response.data['id']
    
        # Make a GET request to the /wallets/ endpoint
        response = authenticated_client.get(api_url(f'wallets/{wallet_id}/'))
    
        assert response.status_code == 200
        assert response.data['owner_id'] == str(test_user[0].id)
        assert response.data['name'] == new_wallet_data['name']
        assert response.data['description'] == new_wallet_data['description']
        assert response.data['co_owners'] == [test_user[1].id]
        assert timezone.now() - timezone.datetime.fromisoformat(response.data['created_at']) < timezone.timedelta(seconds=1)
    

@pytest.mark.django_db
def test_create_wallet_no_auth(api_client, test_user):

    # Make a POST request to the /wallets/ endpoint
    new_wallet_data = {
        'name': 'New Wallet',
        'description': 'New Wallet description'
    }

    response = api_client.post(api_url('wallets/'), new_wallet_data, format='json')

    assert response.status_code == 401

@pytest.mark.django_db
def test_create_wallet_no_name(authenticated_client, test_user):

    check_wallet_create_validations(authenticated_client,
                                name='',
                                co_owners=[],
                                description='New Wallet description',
                                error_field='name',
                                error_message='This field may not be blank.')
    
@pytest.mark.django_db
def test_create_wallet_too_short_name(authenticated_client, test_user):
    
    check_wallet_create_validations(authenticated_client,
                                name='aa',
                                co_owners=[],
                                description='New Wallet description',
                                error_field='name',
                                error_message='Name must be at least 3 characters long')

@pytest.mark.django_db
def test_create_wallet_too_long_name(authenticated_client, test_user):

    check_wallet_create_validations(authenticated_client,
                                name='a'*101,
                                co_owners=[],
                                description='New Wallet description',
                                error_field='name',
                                error_message='Ensure this field has no more than 100 characters.')
    
@pytest.mark.django_db
def test_create_wallet_too_long_description(authenticated_client, test_user):

    check_wallet_create_validations(authenticated_client,
                                name='New Wallet',
                                co_owners=[],
                                description='a'*1001,
                                error_field='description',
                                error_message='Ensure this field has no more than 1000 characters.')
    

@pytest.mark.django_db
def test_create_wallet_duplicated_name(authenticated_client, test_user):
        
    # Create a wallet for the user
    Wallet.objects.create(name='New Wallet', description='New Wallet description', owner=test_user[0])

    assert Wallet.objects.count() == 1

    check_wallet_create_validations(authenticated_client,
                                name='New Wallet',
                                co_owners=[],
                                description='New Wallet description',
                                error_field='name',
                                error_message='Wallet with this Owner and Name already exists.',
                                other_wallets=1)
    

@pytest.mark.django_db
def test_create_wallet_owner_same_as_co_owner(authenticated_client, test_user):
        
    check_wallet_create_validations(authenticated_client,
                                name='New Wallet',
                                co_owners=[test_user[0].id],
                                description='New Wallet description',
                                error_field='co_owners',
                                error_message='Owner cannot be a co-owner of the wallet.')


@pytest.mark.django_db
def test_update_wallet(authenticated_client, test_user, test_wallets):

    # Make a PUT request to the /wallets/1/ endpoint
    wallet_to_update = test_wallets[1]

    wallet_data = {
        'name': 'Updated Wallet',
        'description': 'Updated Wallet description',
        'co_owners': [2]
    }

    response = authenticated_client.put(api_url(f'wallets/{wallet_to_update.id}/'), wallet_data, format='json')

    assert response.status_code == 200
    assert response.data['owner_id'] == wallet_to_update.owner.id
    assert response.data['name'] == wallet_data['name']
    assert response.data['description'] == wallet_data['description']
    assert response.data['co_owners'] == wallet_data.get('co_owners', [])

    # Make a GET request to the /wallets/1/ endpoint
    response = authenticated_client.get(api_url(f'wallets/{wallet_to_update.id}/'))

    assert response.status_code == 200
    assert response.data['owner_id'] == str(wallet_to_update.owner.id)
    assert response.data['name'] == wallet_data['name']
    assert response.data['description'] == wallet_data['description']
    assert response.data['co_owners'] == wallet_data.get('co_owners', [])
    assert timezone.now() - timezone.datetime.fromisoformat(response.data['updated_at']) < timezone.timedelta(seconds=1) 

@pytest.mark.django_db
def test_update_wallet_no_auth(api_client, test_user, test_wallets):
    
    # Make a PUT request to the /wallets/1/ endpoint
    wallet_to_update = test_wallets[1]

    wallet_data = {
        'name': 'Updated Wallet',
        'description': 'Updated Wallet description'
    }

    response = api_client.put(api_url(f'wallets/{wallet_to_update.id}/'), wallet_data, format='json')

    assert response.status_code == 401

@pytest.mark.django_db
def test_update_wallet_no_name(authenticated_client, test_user, test_wallets):

    check_wallet_update_validations(authenticated_client,
                                wallet_id=test_wallets[1].id,
                                name='',
                                co_owners=[],
                                description='Updated Wallet description',
                                error_field='name',
                                error_message='This field may not be blank.',
                                test_wallets=test_wallets)
    
@pytest.mark.django_db
def test_update_wallet_too_short_name(authenticated_client, test_user, test_wallets):

    check_wallet_update_validations(authenticated_client,
                                wallet_id=test_wallets[1].id,
                                name='aa',
                                co_owners=[],
                                description='Updated Wallet description',
                                error_field='name',
                                error_message='Name must be at least 3 characters long',
                                test_wallets=test_wallets)
    
@pytest.mark.django_db
def test_update_wallet_too_long_name(authenticated_client, test_user, test_wallets):

    check_wallet_update_validations(authenticated_client,
                                wallet_id=test_wallets[1].id,
                                name='a'*101,
                                co_owners=[],
                                description='Updated Wallet description',
                                error_field='name',
                                error_message='Ensure this field has no more than 100 characters.',
                                test_wallets=test_wallets)
    
@pytest.mark.django_db
def test_update_wallet_too_long_description(authenticated_client, test_user, test_wallets):

    check_wallet_update_validations(authenticated_client,
                                wallet_id=test_wallets[1].id,
                                name='Updated Wallet',
                                co_owners=[],
                                description='a'*1001,
                                error_field='description',
                                error_message='Ensure this field has no more than 1000 characters.',
                                test_wallets=test_wallets)
    
@pytest.mark.django_db
def test_update_wallet_duplicated_name(authenticated_client, test_user, test_wallets):
    
        # Create a wallet for the user
        Wallet.objects.create(name='Updated Wallet', description='Updated Wallet description', owner=test_user[0])
        
        #Check if wallet was created, but not by counting all wallets, but by checking if wallet with the name exists
        assert Wallet.objects.filter(name='Updated Wallet').exists()

        check_wallet_update_validations(authenticated_client,
                                    wallet_id=test_wallets[0].id,
                                    name='Updated Wallet',
                                    co_owners=[],
                                    description='Updated Wallet description',
                                    error_field='name',
                                    error_message='Wallet with this Owner and Name already exists.',
                                    test_wallets=test_wallets,
                                    other_wallets=1)
        
@pytest.mark.django_db
def test_update_wallet_owner_same_as_co_owner(authenticated_client, test_user, test_wallets):
    
    check_wallet_update_validations(authenticated_client,
                                wallet_id=test_wallets[0].id,
                                name='Updated Wallet',
                                co_owners=[test_user[0].id],
                                description='Updated Wallet description',
                                error_field='co_owners',
                                error_message='Owner cannot be a co-owner of the wallet.',
                                test_wallets=test_wallets)
    
@pytest.mark.django_db
def test_delete_wallet(authenticated_client, test_user, test_wallets):
        
        # Make a DELETE request to the /wallets/1/ endpoint
        wallet_to_delete = test_wallets[1]
    
        response = authenticated_client.delete(api_url(f'wallets/{wallet_to_delete.id}/'))
    
        assert response.status_code == 204
        assert Wallet.objects.count() == len(test_wallets) - 1
    
        # Make a GET request to the /wallets/1/ endpoint
        response = authenticated_client.get(api_url(f'wallets/{wallet_to_delete.id}/'))
    
        assert response.status_code == 404

@pytest.mark.django_db
def test_delete_wallet_no_auth(api_client, test_user, test_wallets):
        
        # Make a DELETE request to the /wallets/1/ endpoint
        wallet_to_delete = test_wallets[1]
    
        response = api_client.delete(api_url(f'wallets/{wallet_to_delete.id}/'))
    
        assert response.status_code == 401
        assert Wallet.objects.count() == len(test_wallets)    

def check_wallet_create_validations(authenticated_client, name, co_owners, description, error_field, error_message, other_wallets = 0):
        
    # Make a POST request to the /wallets/ endpoint
    new_wallet_data = {
        'name': name,
        'co_owners': co_owners,
        'description': description
    }

    response = authenticated_client.post(api_url('wallets/'), new_wallet_data, format='json')

    assert response.status_code == 400
    assert response.data.get(error_field) is not None
    assert str(response.data[error_field][0]) == error_message

    assert Wallet.objects.count() == other_wallets


def check_wallet_update_validations(authenticated_client, wallet_id, name, co_owners, description, error_field, error_message, test_wallets, other_wallets = 0):
    
    # Make a PUT request to the /wallets/1/ endpoint
    wallet_data = {
        'name': name,
        'co_owners': co_owners,
        'description': description
    }

    response = authenticated_client.put(api_url(f'wallets/{wallet_id}/'), wallet_data, format='json')

    assert response.status_code == 400
    assert response.data.get(error_field) is not None
    assert str(response.data[error_field][0]) == error_message
        
    assert Wallet.objects.count() == len(test_wallets) + other_wallets

