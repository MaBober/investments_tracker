import pytest

from decimal import Decimal

from django.utils import timezone
from django.utils.dateparse import parse_datetime

from wallets.models import Withdrawal, Deposit, Account, Wallet, Currency

from wallets.tests.test_fixture import test_user, authenticated_client, api_client, admin_logged_client, api_url, test_currencies, test_countries
from wallets.tests.account.test_fixture import test_accounts, test_account_types, test_account_institution_types, test_institution
from wallets.tests.wallet.test_fixture import test_wallets
from wallets.tests.deposit.test_fixture import test_deposits
from wallets.tests.withdrawal.test_fixture import test_withdrawals


@pytest.mark.django_db
def test_get_withdrawals(admin_logged_client, test_withdrawals):
    response = admin_logged_client.get(api_url('withdrawals/'))

    assert response.status_code == 200
    assert response.data['count'] == len(test_withdrawals)

    assert response.data['results'][0]['amount'] == "{:.2f}".format(test_withdrawals[0].amount)
    assert response.data['results'][0]['currency'] == test_withdrawals[0].currency.code
    assert response.data['results'][0]['description'] == test_withdrawals[0].description
    assert response.data['results'][0]['withdrawn_at'] == test_withdrawals[0].withdrawn_at.astimezone(timezone.get_current_timezone()).isoformat()
    assert response.data['results'][0]['wallet_id'] == test_withdrawals[0].wallet.id
    assert response.data['results'][0]['account_id'] == test_withdrawals[0].account.id
    assert response.data['results'][0]['user_id'] == test_withdrawals[0].user.id
    assert response.data['results'][0]['created_at'] == test_withdrawals[0].created_at.astimezone(timezone.get_current_timezone()).isoformat()
    assert response.data['results'][0]['updated_at'] == test_withdrawals[0].updated_at.astimezone(timezone.get_current_timezone()).isoformat()

@pytest.mark.django_db
def test_get_withdrawals_no_auth(api_client):

    response = api_client.get(api_url('withdrawals/'))

    assert response.status_code == 401
    assert response.data['detail'] == 'Authentication credentials were not provided.'

@pytest.mark.django_db
def test_get_withdrawals_no_admin(authenticated_client):

    response = authenticated_client.get(api_url('withdrawals/'))

    assert response.status_code == 403
    assert response.data['detail'] == 'You do not have permission to perform this action.'


@pytest.mark.django_db
def test_get_withdrawal_owner(api_client, test_user, test_withdrawals):

    withdrawal_to_test = test_withdrawals[0]

    api_client.force_authenticate(user=test_withdrawals[0].user)

    response = api_client.get(api_url(f'withdrawals/{withdrawal_to_test.id}/'))

    assert response.status_code == 200
    assert response.data['amount'] == "{:.2f}".format(test_withdrawals[0].amount)
    assert response.data['currency'] == test_withdrawals[0].currency.code
    assert response.data['description'] == test_withdrawals[0].description
    assert response.data['withdrawn_at'] == test_withdrawals[0].withdrawn_at.astimezone(timezone.get_current_timezone()).isoformat()
    assert response.data['wallet_id'] == test_withdrawals[0].wallet.id
    assert response.data['account_id'] == test_withdrawals[0].account.id
    assert response.data['user_id'] == test_withdrawals[0].user.id
    assert response.data['created_at'] == test_withdrawals[0].created_at.astimezone(timezone.get_current_timezone()).isoformat()
    assert response.data['updated_at'] == test_withdrawals[0].updated_at.astimezone(timezone.get_current_timezone()).isoformat()


@pytest.mark.django_db
def test_get_withdrawal_no_auth(api_client, test_user, test_withdrawals):

    withdrawal_to_test = test_withdrawals[0]
    response = api_client.get(api_url(f'withdrawals/{withdrawal_to_test.id}/'))

    assert response.status_code == 401
    assert response.data['detail'] == 'Authentication credentials were not provided.'


@pytest.mark.django_db
def test_get_withdrawal_not_found(admin_logged_client, test_withdrawals):

    response = admin_logged_client.get(api_url('withdrawals/100/'))

    assert response.status_code == 404
    assert str(response.data['detail']) == 'No Withdrawal matches the given query.'


@pytest.mark.django_db
def test_get_withdrawal_no_creator(api_client, test_user, test_withdrawals):

    withdrawal_to_test = test_withdrawals[0]
    api_client.force_authenticate(user=test_user[1])

    response = api_client.get(api_url(f'withdrawals/{withdrawal_to_test.id}/'))

    assert response.status_code == 403
    assert response.data['detail'] == 'You do not have permission to perform this action.'


@pytest.mark.django_db
def test_create_withdrawal_account_owner(api_client, test_user, test_accounts, test_currencies, test_wallets):

    # Prepare data
    test_wallets[0].owner = test_user[0]
    test_wallets[0].co_owners.clear()
    test_wallets[0].save()

    test_accounts[0].owner = test_user[0]
    test_accounts[0].co_owners.clear()
    test_accounts[0].save()

    #Make deposit
    new_deposit = Deposit.objects.create(
        wallet=test_wallets[0],
        account=test_accounts[0],
        user=test_user[0],
        amount=1000.00,
        currency=test_currencies[0],
        description='Deposit 1',
        deposited_at=timezone.now()
    )

    print(test_accounts[0].get_balance(test_currencies[0]))
    assert test_accounts[0].get_balance(test_currencies[0]) == new_deposit.amount

    withdrawal_data = {
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'description': 'Withdrawal 1',
        'withdrawn_at': timezone.now()
    }

    api_client.force_authenticate(user=test_user[0])
    response = api_client.post(api_url('withdrawals/'), withdrawal_data)

    assert Withdrawal.objects.count() == 1

    assert response.status_code == 201
    assert response.data['amount'] == "{:.2f}".format(withdrawal_data['amount'])
    assert response.data['currency'] == withdrawal_data['currency']
    assert response.data['description'] == withdrawal_data['description']
    assert parse_datetime(response.data['withdrawn_at']) == withdrawal_data['withdrawn_at']
    assert response.data['wallet'] == withdrawal_data['wallet']
    assert response.data['account'] == withdrawal_data['account']
    assert response.data['user_id'] == test_user[0].id

    account = Account.objects.get(id=test_accounts[0].id)

    assert account.get_balance(new_deposit.currency) == new_deposit.amount - Decimal(withdrawal_data['amount'])


@pytest.mark.django_db
def test_create_withdrawal_account_co_owner(api_client, test_user, test_accounts, test_currencies, test_wallets):
    
        # Prepare data
        test_wallets[0].owner = test_user[0]
        test_wallets[0].co_owners.clear()
        test_wallets[0].co_owners.add(test_user[1])
        test_wallets[0].save()
    
        test_accounts[0].owner = test_user[0]
        test_accounts[0].co_owners.clear()
        test_accounts[0].co_owners.add(test_user[1])
        test_accounts[0].save()
    
        #Make deposit
        new_deposit = Deposit.objects.create(
            wallet=test_wallets[0],
            account=test_accounts[0],
            user=test_user[0],
            amount=1000.00,
            currency=test_currencies[0],
            description='Deposit 1',
            deposited_at=timezone.now()
        )
    
        assert test_accounts[0].current_balance == new_deposit.amount
    
        withdrawal_data = {
            'wallet': test_wallets[0].id,
            'account': test_accounts[0].id,
            'amount': 100.00,
            'currency': test_currencies[0].code,
            'description': 'Withdrawal 1',
            'withdrawn_at': timezone.now()
        }
    
        api_client.force_authenticate(user=test_user[1])
        response = api_client.post(api_url('withdrawals/'), withdrawal_data)
    
        assert Withdrawal.objects.count() == 1
    
        assert response.status_code == 201
        assert response.data['amount'] == "{:.2f}".format(withdrawal_data['amount'])
        assert response.data['currency'] == withdrawal_data['currency']
        assert response.data['description'] == withdrawal_data['description']
        assert parse_datetime(response.data['withdrawn_at']) == withdrawal_data['withdrawn_at']
        assert response.data['wallet'] == withdrawal_data['wallet']
        assert response.data['account'] == withdrawal_data['account']
        assert response.data['user_id'] == test_user[1].id
    
        account = Account.objects.get(id=test_accounts[0].id)
    
        assert account.get_balance(new_deposit.currency) == new_deposit.amount - Decimal(withdrawal_data['amount'])


@pytest.mark.django_db
def test_create_withdrawal_account_not_owner_nor_co_owner(api_client, test_user, test_accounts, test_currencies, test_wallets):

    # Prepare data
    test_wallets[0].owner = test_user[0]
    test_wallets[0].co_owners.clear()
    test_wallets[0].save()

    test_accounts[0].owner = test_user[1]
    test_accounts[0].co_owners.clear()
    test_accounts[0].save()

    withdrawal_data = {
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'description': 'Withdrawal 1',
        'withdrawn_at': timezone.now()
    }

    check_withdrawal_create_validations(api_client,
                                        withdrawal_data,
                                        'account',
                                        'You do not own this account.',
                                        user_to_authenticate=test_user[0])
    

@pytest.mark.django_db
def test_create_withdrawal_no_auth(api_client, test_user, test_accounts, test_currencies, test_wallets):

    withdrawal_data = {
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'description': 'Withdrawal 1',
        'withdrawn_at': timezone.now()
    }

    response = api_client.post(api_url('withdrawals/'), withdrawal_data)

    assert response.status_code == 401
    assert response.data['detail'] == 'Authentication credentials were not provided.'
    

@pytest.mark.django_db
def test_create_withdrawal_account_no_wallet(api_client, test_user, test_accounts, test_currencies, test_wallets):

    withdrawal_data = {
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'description': 'Withdrawal 1',
        'withdrawn_at': timezone.now()
    }

    check_withdrawal_create_validations(api_client,
                                        withdrawal_data,
                                        'wallet',
                                        'This field is required.',
                                        user_to_authenticate=test_accounts[0].owner)
    

@pytest.mark.django_db
def test_create_withdrawal_not_exisitng_wallet(api_client, test_user, test_accounts, test_currencies, test_wallets):
    
    withdrawal_data = {
        'wallet': 100,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'description': 'Withdrawal 1',
        'withdrawn_at': timezone.now()
    }

    check_withdrawal_create_validations(api_client,
                                        withdrawal_data,
                                        'wallet',
                                        'Invalid pk "100" - object does not exist.',
                                        user_to_authenticate=test_accounts[0].owner)
    

@pytest.mark.django_db
def test_create_withdrawal_no_account(api_client, test_user, test_accounts, test_currencies, test_wallets):
        
    withdrawal_data = {
        'wallet': test_wallets[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'description': 'Withdrawal 1',
        'withdrawn_at': timezone.now()
    }

    check_withdrawal_create_validations(api_client,
                                        withdrawal_data,
                                        'account',
                                        'This field is required.',
                                        user_to_authenticate=test_wallets[0].owner)
            

@pytest.mark.django_db
def test_create_withdrawal_not_exisitng_account(api_client, test_user, test_accounts, test_currencies, test_wallets):
            
    withdrawal_data = {
        'wallet': test_wallets[0].id,
        'account': 100,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'description': 'Withdrawal 1',
        'withdrawn_at': timezone.now()
    }

    check_withdrawal_create_validations(api_client,
                                        withdrawal_data,
                                        'account',
                                        'Invalid pk "100" - object does not exist.',
                                        user_to_authenticate=test_wallets[0].owner)
            

@pytest.mark.django_db
def test_create_withdrawal_from_account_not_matching_wallet(api_client, test_user, test_accounts, test_currencies, test_wallets):
                    
    # Prepare data

    Deposit.objects.create(
        wallet=test_wallets[1],
        account=test_accounts[1],
        user=test_wallets[1].owner,
        amount=1000.00,
        currency=test_currencies[0],
        description='Deposit 1',
        deposited_at=timezone.now()
    )

    test_wallets[0].accounts.clear()
    test_wallets[0].save()

    test_accounts[1].owner = test_user[0]
    test_accounts[1].save()


    withdrawal_data = {
        'wallet': test_wallets[0].id,
        'account': test_accounts[1].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'description': 'Withdrawal 1',
        'withdrawn_at': timezone.now()
    }

    check_withdrawal_create_validations(api_client,
                                        withdrawal_data,
                                        'account_wallet_mismatch',
                                        'The account must belong to the wallet to make a withdrawal.',
                                        user_to_authenticate=test_wallets[0].owner
                                        )
    

@pytest.mark.django_db
def test_create_withdrawal_no_amount(api_client, test_user, test_accounts, test_currencies, test_wallets):
                            
    withdrawal_data = {
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'currency': test_currencies[0].code,
        'description': 'Withdrawal 1',
        'withdrawn_at': timezone.now()
    }

    check_withdrawal_create_validations(api_client,
                                        withdrawal_data,
                                        'amount',
                                        'This field is required.',
                                        user_to_authenticate=test_accounts[0].owner)
    
@pytest.mark.django_db
def test_create_withdrawal_amount_empty(api_client, test_user, test_accounts, test_currencies, test_wallets):
                                    
    withdrawal_data = {
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': '',
        'currency': test_currencies[0].code,
        'description': 'Withdrawal 1',
        'withdrawn_at': timezone.now()
    }

    check_withdrawal_create_validations(api_client,
                                        withdrawal_data,
                                        'amount',
                                        'A valid number is required.',
                                        user_to_authenticate=test_accounts[0].owner)
    

@pytest.mark.django_db
def test_create_withdrawal_amount_negative(api_client, test_user, test_accounts, test_currencies, test_wallets):
                                            
    withdrawal_data = {
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': -100.00,
        'currency': test_currencies[0].code,
        'description': 'Withdrawal 1',
        'withdrawn_at': timezone.now()
    }

    check_withdrawal_create_validations(api_client,
                                        withdrawal_data,
                                        'amount',
                                        'Ensure this value is greater than or equal to 0.01.',
                                        user_to_authenticate=test_accounts[0].owner)
    

@pytest.mark.django_db
def test_create_withdrawal_amount_string(api_client, test_user, test_accounts, test_currencies, test_wallets):
                                                    
    withdrawal_data = {
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': '10a0.00',
        'currency': test_currencies[0].code,
        'description': 'Withdrawal 1',
        'withdrawn_at': timezone.now()
    }

    check_withdrawal_create_validations(api_client,
                                        withdrawal_data,
                                        'amount',
                                        'A valid number is required.',
                                        user_to_authenticate=test_accounts[0].owner)


@pytest.mark.django_db
def test_create_withdrawal_no_sufficient_funds(api_client, test_user, test_accounts, test_currencies, test_wallets):
                                                            
    withdrawal_data = {
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'description': 'Withdrawal 1',
        'withdrawn_at': timezone.now()
    }

    check_withdrawal_create_validations(api_client,
                                        withdrawal_data,
                                        'amount',
                                        'Insufficient funds in the account.',
                                        user_to_authenticate=test_accounts[0].owner,
                                        deposit=50.00)
    

@pytest.mark.django_db
def test_create_withdrawal_no_currency(api_client, test_user, test_accounts, test_currencies, test_wallets):
                                                                
    withdrawal_data = {
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'description': 'Withdrawal 1',
        'withdrawn_at': timezone.now()
    }

    check_withdrawal_create_validations(api_client,
                                        withdrawal_data,
                                        'currency',
                                        'This field is required.',
                                        user_to_authenticate=test_accounts[0].owner)
    

@pytest.mark.django_db
def test_create_withdrawal_not_exisitng_currency(api_client, test_user, test_accounts, test_currencies, test_wallets):
                                                                
    withdrawal_data = {
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': 'USA',
        'description': 'Withdrawal 1',
        'withdrawn_at': timezone.now()
    }

    check_withdrawal_create_validations(api_client,
                                        withdrawal_data,
                                        'currency',
                                        'USA is a wrong currency. Please provide a valid currency.',
                                        user_to_authenticate=test_accounts[0].owner)


@pytest.mark.django_db
def test_create_withdrawal_currency_not_matching_account(api_client, test_user, test_accounts, test_currencies, test_wallets):
                                                                    
    withdrawal_data = {
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[1].code,
        'description': 'Withdrawal 1',
        'withdrawn_at': timezone.now()
    }

    check_withdrawal_create_validations(api_client,
                                        withdrawal_data,
                                        'currency',
                                        'This currency is not supported by this account.',
                                        user_to_authenticate=test_accounts[0].owner)


@pytest.mark.django_db
def test_create_withdrawal_too_long_description(api_client, test_user, test_accounts, test_currencies, test_wallets):

    withdrawal_data = {
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'description': 'a' * 1001,
        'withdrawn_at': timezone.now()
    }

    check_withdrawal_create_validations(api_client,
                                        withdrawal_data,
                                        'description',
                                        'Ensure this field has no more than 1000 characters.',
                                        user_to_authenticate=test_accounts[0].owner)
    

@pytest.mark.django_db
def test_create_withdrawal_no_withdrawn_at(api_client, test_user, test_accounts, test_currencies, test_wallets):
                                                                        
    withdrawal_data = {
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'description': 'Withdrawal 1',
    }

    check_withdrawal_create_validations(api_client,
                                        withdrawal_data,
                                        'withdrawn_at',
                                        'This field is required.',
                                        user_to_authenticate=test_accounts[0].owner)
    

@pytest.mark.django_db
def test_create_widthrawal_witdrawn_at_no_date(api_client, test_user, test_accounts, test_currencies, test_wallets):
                                                                                
    withdrawal_data = {
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'description': 'Withdrawal 1',
        'withdrawn_at': 'AAAA'
    }

    check_withdrawal_create_validations(api_client,
                                        withdrawal_data,
                                        'withdrawn_at',
                                        'Datetime has wrong format. Use one of these formats instead: YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z].',
                                        user_to_authenticate=test_accounts[0].owner)
        
@pytest.mark.django_db
def test_create_withdrawal_witdrawn_at_future_date(api_client, test_user, test_accounts, test_currencies, test_wallets):
                                                                                    
    withdrawal_data = {
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'description': 'Withdrawal 1',
        'withdrawn_at': timezone.now() + timezone.timedelta(days=1)
    }

    check_withdrawal_create_validations(api_client,
                                        withdrawal_data,
                                        'withdrawn_at',
                                        'Date cannot be in the future.',
                                        user_to_authenticate=test_accounts[0].owner,
                                        deposit=200)
        
@pytest.mark.django_db
def test_update_withdrawal_owner(api_client, test_user, test_accounts, test_currencies, test_wallets, test_withdrawals):

    withdrawal_to_update = test_withdrawals[0]

    withdrawal_data = {
        'wallet': withdrawal_to_update.wallet.id,
        'account': withdrawal_to_update.account.id,
        'amount': 100.00,
        'currency': withdrawal_to_update.currency.code,
        'description': 'Withdrawal 1',
        'withdrawn_at': timezone.now()
    }

    api_client.force_authenticate(user=withdrawal_to_update.user)

    response = api_client.put(api_url(f'withdrawals/{withdrawal_to_update.id}/'), withdrawal_data)

    assert response.status_code == 405

@pytest.mark.django_db
def test_delete_withdrawal_owner(api_client, test_user, test_accounts, test_currencies, test_wallets, test_withdrawals):
    
    withdrawal_to_delete = test_withdrawals[0]

    api_client.force_authenticate(user=withdrawal_to_delete.user)

    response = api_client.delete(api_url(f'withdrawals/{withdrawal_to_delete.id}/'))

    assert response.status_code == 204
    assert Withdrawal.objects.count() == len(test_withdrawals) - 1

    response = api_client.get(api_url(f'withdrawals/{withdrawal_to_delete.id}/'))

    assert response.status_code == 404

@pytest.mark.django_db
def test_delete_withdrawal_no_auth(api_client, test_user, test_accounts, test_currencies, test_wallets, test_withdrawals):
    
    withdrawal_to_delete = test_withdrawals[0]

    response = api_client.delete(api_url(f'withdrawals/{withdrawal_to_delete.id}/'))

    assert response.status_code == 401
    assert response.data['detail'] == 'Authentication credentials were not provided.'


@pytest.mark.django_db
def test_delete_withdrawal_not_found(admin_logged_client, test_withdrawals):

    response = admin_logged_client.delete(api_url('withdrawals/100/'))

    assert response.status_code == 404
    assert str(response.data['detail']) == 'No Withdrawal matches the given query.'


@pytest.mark.django_db
def test_delete_withdrawal_no_creator(api_client, test_user, test_withdrawals):

    withdrawal_to_delete = test_withdrawals[0]
    api_client.force_authenticate(user=test_user[1])

    response = api_client.delete(api_url(f'withdrawals/{withdrawal_to_delete.id}/'))

    assert response.status_code == 403
    assert response.data['detail'] == 'You do not have permission to perform this action.'


def check_withdrawal_create_validations(api_client, withdrawal_data, error_field, error_message, user_to_authenticate=None, deposit=None):

    if user_to_authenticate:
        api_client.force_authenticate(user=user_to_authenticate)

    if deposit:
        new_deposit = Deposit.objects.create(
            wallet=Wallet.objects.get(id=withdrawal_data['wallet']),
            account=Account.objects.get(id=withdrawal_data['account']),
            user=user_to_authenticate,
            amount=deposit,
            currency=Currency.objects.get(code=withdrawal_data['currency']),
            description='Deposit 1',
            deposited_at=timezone.now()
        )

    response = api_client.post(api_url('withdrawals/'), withdrawal_data)

    assert Withdrawal.objects.count() == 0

    assert response.status_code == 400
    assert str(response.data[error_field][0]) == error_message