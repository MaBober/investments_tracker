import pytest

from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from wallets.models import Deposit

from wallets.tests.test_fixture import test_user, authenticated_client, api_client, admin_logged_client, api_url, test_currencies, test_countries
from wallets.tests.account.test_fixture import test_accounts, test_account_types, test_account_institution_types, test_institution
from wallets.tests.wallet.test_fixture import test_wallets
from wallets.tests.deposit.test_fixture import test_deposits


@pytest.mark.django_db
def test_get_deposits(admin_logged_client, test_deposits):

    response = admin_logged_client.get(api_url('deposits/'))

    assert response.status_code == 200
    assert response.data['count'] == len(test_deposits)
    assert response.data['results'][0]['amount'] == "{:.2f}".format(test_deposits[0].amount)
    assert response.data['results'][0]['description'] == test_deposits[0].description
    assert response.data['results'][0]['currency'] == test_deposits[0].currency.code
    assert response.data['results'][0]['deposited_at'] == test_deposits[0].deposited_at.astimezone(timezone.get_current_timezone()).isoformat()
    assert response.data['results'][0]['wallet_id'] == test_deposits[0].wallet.id
    assert response.data['results'][0]['account_id'] == test_deposits[0].account.id
    assert response.data['results'][0]['user_id'] == test_deposits[0].user.id
    assert response.data['results'][0]['created_at'] == test_deposits[0].created_at.astimezone(timezone.get_current_timezone()).isoformat()
    assert response.data['results'][0]['updated_at'] == test_deposits[0].updated_at.astimezone(timezone.get_current_timezone()).isoformat()


@pytest.mark.django_db
def test_get_deposits_no_auth(api_client):

    response = api_client.get(api_url('deposits/'))

    assert response.status_code == 401
    assert response.data['detail'] == 'Authentication credentials were not provided.'


@pytest.mark.django_db
def test_get_deposits_no_admin(authenticated_client):

    response = authenticated_client.get(api_url('deposits/'))

    assert response.status_code == 403
    assert response.data['detail'] == 'You do not have permission to perform this action.'


@pytest.mark.django_db
def test_get_deposit_owner(api_client, test_deposits):

    deposit_to_test = test_deposits[1]
    api_client.force_authenticate(user=deposit_to_test.user)

    response = api_client.get(api_url(f'deposits/{deposit_to_test.id}/'))

    assert response.status_code == 200
    assert response.data['amount'] == "{:.2f}".format(deposit_to_test.amount)
    assert response.data['description'] == deposit_to_test.description
    assert response.data['currency'] == deposit_to_test.currency.code
    assert response.data['deposited_at'] == deposit_to_test.deposited_at.astimezone(timezone.get_current_timezone()).isoformat()
    assert response.data['wallet_id'] == deposit_to_test.wallet.id
    assert response.data['account_id'] == deposit_to_test.account.id
    assert response.data['user_id'] == deposit_to_test.user.id
    assert response.data['created_at'] == deposit_to_test.created_at.astimezone(timezone.get_current_timezone()).isoformat()
    assert response.data['updated_at'] == deposit_to_test.updated_at.astimezone(timezone.get_current_timezone()).isoformat()


@pytest.mark.django_db
def test_get_deposit_owner_no_auth(api_client, test_deposits):

    deposit_to_test = test_deposits[1]
    response = api_client.get(api_url(f'deposits/{deposit_to_test.id}/'))

    assert response.status_code == 401
    assert response.data['detail'] == 'Authentication credentials were not provided.'

@pytest.mark.django_db
def test_get_deposit_not_found(authenticated_client):

    response = authenticated_client.get(api_url('deposits/100/'))

    assert response.status_code == 404
    assert response.data['detail'] == 'No Deposit matches the given query.'

@pytest.mark.django_db
def test_get_deposit_no_creator(api_client, test_deposits, test_user):

    deposit_to_test = test_deposits[0]
    deposit_to_test.user = test_user[0]
    deposit_to_test.save()

    api_client.force_authenticate(user=test_user[1])
    response = api_client.get(api_url(f'deposits/{deposit_to_test.id}/'))

    assert response.status_code == 403
    assert response.data['detail'] == 'You do not have permission to perform this action.'


@pytest.mark.django_db
def test_create_deposit_owner(api_client, test_user, test_wallets, test_accounts, test_currencies):

    test_wallets[0].owner = test_user[0]
    test_wallets[0].co_owners.clear()
    test_wallets[0].save()

    test_accounts[0].owner = test_user[0]
    test_accounts[0].co_owners.clear()
    test_accounts[0].save()


    deposit_data = {
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'description': 'Test deposit',
        'deposited_at': timezone.now()
    }

    api_client.force_authenticate(user=test_user[0])
    response = api_client.post(api_url('deposits/'), data=deposit_data)

    assert response.status_code == 201
    assert response.data['amount'] == "{:.2f}".format(deposit_data['amount'])
    assert response.data['description'] == deposit_data['description']
    assert response.data['currency'] == deposit_data['currency']
    assert parse_datetime(response.data['deposited_at']) == deposit_data['deposited_at']
    assert response.data['wallet'] == deposit_data['wallet']
    assert response.data['account'] == deposit_data['account']
    assert response.data['user_id'] == test_user[0].id


@pytest.mark.django_db
def test_create_deposit_co_owner(api_client, test_user, test_wallets, test_accounts, test_currencies):

    test_wallets[0].owner = test_user[0]
    test_wallets[0].co_owners.clear()
    test_wallets[0].co_owners.add(test_user[1])
    test_wallets[0].save()

    test_accounts[0].owner = test_user[0]
    test_accounts[0].co_owners.clear()
    test_accounts[0].co_owners.add(test_user[1])
    test_accounts[0].save()

    deposit_data = {
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'description': 'Test deposit',
        'deposited_at': timezone.now()
    }

    api_client.force_authenticate(user=test_user[1])
    response = api_client.post(api_url('deposits/'), data=deposit_data)

    assert response.status_code == 201
    assert response.data['amount'] == "{:.2f}".format(deposit_data['amount'])
    assert response.data['description'] == deposit_data['description']
    assert response.data['currency'] == deposit_data['currency']
    assert parse_datetime(response.data['deposited_at']) == deposit_data['deposited_at']
    assert response.data['wallet'] == deposit_data['wallet']
    assert response.data['account'] == deposit_data['account']
    assert response.data['user_id'] == test_user[1].id


@pytest.mark.django_db
def test_create_deposit_account_not_owner_nor_co_owner(api_client, test_user, test_wallets, test_accounts, test_currencies):

    test_wallets[0].owner = test_user[0]
    test_wallets[0].co_owners.clear()
    test_wallets[0].save()

    test_accounts[0].owner = test_user[1]
    test_accounts[0].co_owners.clear()
    test_accounts[0].save()

    deposit_data = {
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'description': 'Test deposit',
        'deposited_at': timezone.now()
    }

    check_deposit_create_validations(api_client,
                                     deposit_data,
                                    'account',
                                    'You do not own this account.',
                                     test_user[0])

@pytest.mark.django_db
def test_create_deposit_no_auth(api_client, test_wallets, test_accounts, test_currencies):

    deposit_data = {
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'description': 'Test deposit',
        'deposited_at': timezone.now()
    }

    response = api_client.post(api_url('deposits/'), data=deposit_data)

    assert response.status_code == 401
    assert response.data['detail'] == 'Authentication credentials were not provided.'


@pytest.mark.django_db
def test_create_deposit_no_wallet(api_client, test_accounts, test_currencies):
    
    deposit_data = {
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'description': 'Test deposit',
        'deposited_at': timezone.now()
    }

    check_deposit_create_validations(api_client,
                                     deposit_data,
                                    'wallet',
                                     'This field is required.',
                                     test_accounts[0].owner)


@pytest.mark.django_db
def test_create_deposit_non_existing_wallet(api_client, test_accounts, test_currencies):
        
    deposit_data = {
        'wallet': 100,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'description': 'Test deposit',
        'deposited_at': timezone.now()
    }

    check_deposit_create_validations(api_client,
                                    deposit_data,
                                    'wallet',
                                    'Invalid pk "100" - object does not exist.',
                                    test_accounts[0].owner)


@pytest.mark.django_db
def test_create_deposit_no_account(api_client, test_wallets, test_currencies):
    
    deposit_data = {
        'wallet': test_wallets[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'description': 'Test deposit',
        'deposited_at': timezone.now()
    }

    check_deposit_create_validations(api_client,
                                    deposit_data,
                                    'account',
                                    'This field is required.',
                                    test_wallets[0].owner)


@pytest.mark.django_db
def test_create_deposit_from_account_not_matching_wallet(api_client, test_user, test_wallets, test_accounts, test_currencies):
    
    test_wallets[0].owner = test_user[0]
    test_wallets[0].co_owners.clear()
    test_wallets[0].save()

    test_accounts[1].owner = test_user[0]
    test_accounts[1].co_owners.clear()
    test_accounts[1].wallets.clear()
    test_accounts[1].save()

    deposit_data = {
        'wallet': test_wallets[0].id,
        'account': test_accounts[1].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'description': 'Test deposit',
        'deposited_at': timezone.now()
    }

    check_deposit_create_validations(api_client,
                                    deposit_data,
                                    'account_wallet_mismatch',
                                    'The account must belong to the wallet to make a deposit.',
                                    test_wallets[0].owner)


@pytest.mark.django_db
def test_create_deposit_non_existing_account(api_client, test_wallets, test_currencies):
        
    deposit_data = {
        'wallet': test_wallets[0].id,
        'account': 100,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'description': 'Test deposit',
        'deposited_at': timezone.now()
    }

    check_deposit_create_validations(api_client,
                                    deposit_data,
                                    'account',
                                    'Invalid pk "100" - object does not exist.',
                                    test_wallets[0].owner)


@pytest.mark.django_db
def test_create_deposit_no_amount(api_client, test_wallets, test_accounts, test_currencies):
    
    deposit_data = {
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'currency': test_currencies[0].code,
        'description': 'Test deposit',
        'deposited_at': timezone.now()
    }

    check_deposit_create_validations(api_client,
                                    deposit_data,
                                    'amount',
                                    'This field is required.',
                                    test_wallets[0].owner)


@pytest.mark.django_db
def test_create_deposit_negative_amount(api_client, test_wallets, test_accounts, test_currencies):
    
    deposit_data = {
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': -100.00,
        'currency': test_currencies[0].code,
        'description': 'Test deposit',
        'deposited_at': timezone.now()
    }

    check_deposit_create_validations(api_client,
                                     deposit_data,
                                    'amount',
                                    'Ensure this value is greater than or equal to 0.01.',
                                    test_wallets[0].owner)

@pytest.mark.django_db
def test_create_deposit_zero_amount(api_client, test_wallets, test_accounts, test_currencies):
        
    deposit_data = {
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 0.00,
        'currency': test_currencies[0].code,
        'description': 'Test deposit',
        'deposited_at': timezone.now()
    }

    check_deposit_create_validations(api_client,
                                    deposit_data,
                                    'amount',
                                    'Ensure this value is greater than or equal to 0.01.',
                                    test_wallets[0].owner)


@pytest.mark.django_db
def test_create_deposit_stirng_amount(api_client, test_wallets, test_accounts, test_currencies):
            
    deposit_data = {
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': '100.0a0',
        'currency': test_currencies[0].code,
        'description': 'Test deposit',
        'deposited_at': timezone.now()
    }

    check_deposit_create_validations(api_client,
                                    deposit_data,
                                    'amount',
                                    'A valid number is required.',
                                    test_wallets[0].owner)


@pytest.mark.django_db
def test_create_deposit_no_currency(api_client, test_wallets, test_accounts):
    
    deposit_data = {
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'description': 'Test deposit',
        'deposited_at': timezone.now()
    }

    check_deposit_create_validations(api_client,
                                    deposit_data,
                                    'currency',
                                    'This field is required.',
                                    test_wallets[0].owner)


@pytest.mark.django_db
def test_create_deposit_non_existing_currency(api_client, test_wallets, test_accounts):
        
    deposit_data = {
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': 'ABC',
        'description': 'Test deposit',
        'deposited_at': timezone.now()
    }

    check_deposit_create_validations(api_client,
                                    deposit_data,
                                    'currency',
                                    'ABC is a wrong currency. Please provide a valid currency.',
                                    test_wallets[0].owner)

@pytest.mark.django_db
def test_create_deposit_currency_diffrent_than_account(api_client, test_wallets, test_accounts, test_currencies):
        
    deposit_data = {
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[1].code,
        'description': 'Test deposit',
        'deposited_at': timezone.now()
    }

    check_deposit_create_validations(api_client,
                                    deposit_data,
                                    'currency',
                                    'This currency is not supported by this account.',
                                    test_wallets[0].owner)


@pytest.mark.django_db
def test_create_deposit_too_long_description(api_client, test_wallets, test_accounts, test_currencies):
            
    deposit_data = {
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'description': 'a' * 1001,
        'deposited_at': timezone.now()
    }

    check_deposit_create_validations(api_client,
                                    deposit_data,
                                    'description',
                                    'Ensure this field has no more than 1000 characters.',
                                    test_wallets[0].owner)


@pytest.mark.django_db
def test_create_deposit_no_deposited_at(api_client, test_wallets, test_accounts, test_currencies):
    
    deposit_data = {
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'description': 'Test deposit'
    }

    check_deposit_create_validations(api_client,
                                    deposit_data,
                                    'deposited_at',
                                    'This field is required.',
                                    test_wallets[0].owner)


@pytest.mark.django_db
def test_create_deposit_future_deposited_at(api_client, test_wallets, test_accounts, test_currencies):
    
    deposit_data = {
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'description': 'Test deposit',
        'deposited_at': timezone.now() + timezone.timedelta(days=1)
    }

    check_deposit_create_validations(api_client,
                                     deposit_data,
                                    'deposited_at',
                                    'Date cannot be in the future.',
                                    test_wallets[0].owner)


@pytest.mark.django_db
def test_update_deposit_owner(authenticated_client, test_deposits, test_wallets, test_accounts, test_currencies):

    deposit_to_update = test_deposits[1]

    deposit_data = {
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 1010.00,
        'currency': test_currencies[0].code,
        'description': 'Test deposit updated',
        'deposited_at': timezone.now()
    }

    response = authenticated_client.put(api_url(f'deposits/{deposit_to_update.id}/'), data=deposit_data)

    assert response.status_code == 405

@pytest.mark.django_db
def delete_deposit_owner(api_client, test_deposits):

    deposit_to_delete = test_deposits[1]

    api_client.force_authenticate(user=deposit_to_delete.user)
    response = api_client.delete(api_url(f'deposits/{deposit_to_delete.id}/'))

    assert response.status_code == 204
    assert Deposit.objects.filter(id=deposit_to_delete.id).exists() == False
    assert Deposit.objects.count() == len(test_deposits) - 1


@pytest.mark.django_db
def test_delete_deposit_no_auth(api_client, test_deposits):

    deposit_to_delete = test_deposits[1]
    response = api_client.delete(api_url(f'deposits/{deposit_to_delete.id}/'))

    assert response.status_code == 401
    assert response.data['detail'] == 'Authentication credentials were not provided.'


@pytest.mark.django_db
def test_delete_deposit_not_found(authenticated_client):

    response = authenticated_client.delete(api_url('deposits/100/'))

    assert response.status_code == 404
    assert response.data['detail'] == 'No Deposit matches the given query.'


@pytest.mark.django_db
def test_delete_deposit_no_creator(api_client, test_deposits, test_user):

    deposit_to_delete = test_deposits[0]
    deposit_to_delete.user = test_user[0]
    deposit_to_delete.save()

    api_client.force_authenticate(user=test_user[1])
    response = api_client.delete(api_url(f'deposits/{deposit_to_delete.id}/'))

    assert response.status_code == 403
    assert response.data['detail'] == 'You do not have permission to perform this action.'



def check_deposit_create_validations(api_client, deposit_data, error_field, error_message, user_to_authenticate=None,):
    
    if user_to_authenticate:
        api_client.force_authenticate(user=user_to_authenticate)

    response = api_client.post(api_url('deposits/'), data=deposit_data)


    assert response.status_code == 400
    assert response.data.get(error_field) is not None
    assert str(response.data[error_field][0]) == error_message



#TODO : Add tests for the deposit update validations