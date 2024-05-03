import pytest

from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from wallets.models import MarketAssetTransaction, Deposit, Wallet, Account, Currency

from wallets.tests.test_fixture import test_user, authenticated_client, api_client, admin_logged_client, api_url, test_currencies, test_countries
from wallets.tests.account.test_fixture import test_accounts, test_account_types, test_account_institution_types, test_institution
from wallets.tests.asset.test_fixture import test_asset_types, test_exchange_marketes, test_market_shares
from wallets.tests.wallet.test_fixture import test_wallets
from wallets.tests.deposit.test_fixture import test_deposits
from wallets.tests.transaction.test_fixture import test_market_asset_transactions

@pytest.mark.django_db
def test_market_asset_transactions_list(admin_logged_client, test_market_asset_transactions):

    response = admin_logged_client.get(api_url('market_transactions/'))

    assert response.status_code == 200
    assert response.data['count'] == len(test_market_asset_transactions)

    assert response.data['results'][0]['id'] == test_market_asset_transactions[0].id
    assert response.data['results'][0]['asset'] == test_market_asset_transactions[0].asset.id
    assert response.data['results'][0]['wallet_id'] == test_market_asset_transactions[0].wallet.id
    assert response.data['results'][0]['account_id'] == test_market_asset_transactions[0].account.id
    assert response.data['results'][0]['user_id'] == test_market_asset_transactions[0].user.id
    assert response.data['results'][0]['amount'] == "{:.2f}".format(test_market_asset_transactions[0].amount)
    assert response.data['results'][0]['currency'] == test_market_asset_transactions[0].currency.id
    assert response.data['results'][0]['transaction_type'] == test_market_asset_transactions[0].transaction_type
    assert response.data['results'][0]['price'] == "{:.2f}".format(test_market_asset_transactions[0].price)
    assert response.data['results'][0]['commission'] == "{:.2f}".format(test_market_asset_transactions[0].commission)
    assert response.data['results'][0]['commission_currency'] == test_market_asset_transactions[0].commission_currency.id
    assert response.data['results'][0]['transaction_date'] == test_market_asset_transactions[0].transaction_date.astimezone(timezone.get_current_timezone()).isoformat()


@pytest.mark.django_db
def test_market_asset_transactions_no_auth(api_client):

    response = api_client.get(api_url('market_transactions/'))

    assert response.status_code == 401
    assert response.data['detail'] == "Authentication credentials were not provided."


@pytest.mark.django_db
def test_market_asset_transactions_no_admiin_auth(authenticated_client):

    response = authenticated_client.get(api_url('market_transactions/'))

    assert response.status_code == 403
    assert response.data['detail'] == "You do not have permission to perform this action."


@pytest.mark.django_db
def test_market_asset_transaction_owner(api_client, test_market_asset_transactions):

    transaction_to_test = test_market_asset_transactions[0]
    api_client.force_authenticate(user=transaction_to_test.user)

    response = api_client.get(api_url(f'market_transactions/{transaction_to_test.id}/'))

    assert response.status_code == 200

    assert response.data['id'] == test_market_asset_transactions[0].id
    assert response.data['asset'] == test_market_asset_transactions[0].asset.id
    assert response.data['wallet_id'] == test_market_asset_transactions[0].wallet.id
    assert response.data['account_id'] == test_market_asset_transactions[0].account.id
    assert response.data['user_id'] == test_market_asset_transactions[0].user.id
    assert response.data['amount'] == "{:.2f}".format(test_market_asset_transactions[0].amount)
    assert response.data['currency'] == test_market_asset_transactions[0].currency.id
    assert response.data['transaction_type'] == test_market_asset_transactions[0].transaction_type
    assert response.data['price'] == "{:.2f}".format(test_market_asset_transactions[0].price)
    assert response.data['commission'] == "{:.2f}".format(test_market_asset_transactions[0].commission)
    assert response.data['commission_currency'] == test_market_asset_transactions[0].commission_currency.id
    assert response.data['transaction_date'] == test_market_asset_transactions[0].transaction_date.astimezone(timezone.get_current_timezone()).isoformat()


@pytest.mark.django_db
def test_market_asset_transaction_no_auth(api_client, test_market_asset_transactions):

    transaction_to_test = test_market_asset_transactions[0]

    response = api_client.get(api_url(f'market_transactions/{transaction_to_test.id}/'))

    assert response.status_code == 401
    assert response.data['detail'] == "Authentication credentials were not provided."


@pytest.mark.django_db
def test_market_asset_transaction_no_creator(api_client, test_market_asset_transactions, test_user):

    transaction_to_test = test_market_asset_transactions[0]
    api_client.force_authenticate(user=test_user[1])

    response = api_client.get(api_url(f'market_transactions/{transaction_to_test.id}/'))

    assert response.status_code == 403
    assert response.data['detail'] == "You do not have permission to perform this action."


@pytest.mark.django_db
def test_market_asset_transaction_not_found(api_client):

    response = api_client.get(api_url('market_transactions/100/'))

    assert response.status_code == 404
    assert response.data['detail'] == 'No MarketAssetTransaction matches the given query.'


@pytest.mark.django_db
def test_market_asset_transaction_create_owner(api_client, test_market_shares, test_wallets, test_accounts, test_currencies, test_user):

    test_wallets[0].owner = test_user[0]
    test_wallets[0].co_owners.clear()
    test_wallets[0].save()

    test_accounts[0].owner = test_user[0]
    test_accounts[0].co_owners.clear()
    test_accounts[0].save()

    Deposit.objects.create(wallet=test_wallets[0], account=test_accounts[0], user=test_user[0], amount=10022.00, currency=test_currencies[0], deposited_at=timezone.now())

    data = {
        'code': test_market_shares[0].code,
        'exchange_market': test_market_shares[0].exchange_market.id,
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'currency_price': 1.00,
        'transaction_type': 'B',
        'price': 100.00,
        'commission': 1.00,
        'commission_currency': test_currencies[0].code,
        'commission_currency_price': 2.00,
        'transaction_date': timezone.now().isoformat()
    }

    api_client.force_authenticate(user=test_user[0])
    response = api_client.post(api_url('market_transactions/'), data=data)

    assert response.status_code == 201

    assert response.data['asset_code'] == data['code']
    assert response.data['wallet'] == data['wallet']
    assert response.data['account'] == data['account']
    assert response.data['user_id'] == test_user[0].id
    assert response.data['amount'] == "{:.2f}".format(data['amount'])
    assert response.data['currency'] == data['currency']
    assert response.data['transaction_type'] == data['transaction_type']
    assert response.data['price'] == "{:.2f}".format(data['price'])
    assert response.data['commission'] == "{:.2f}".format(data['commission'])
    assert response.data['commission_currency'] == data['commission_currency']
    assert response.data['transaction_date'] == parse_datetime(data['transaction_date']).astimezone(timezone.get_current_timezone()).isoformat()

    new_transaction = MarketAssetTransaction.objects.get(id=response.data['id'])
    assert new_transaction.asset.code == data['code']
    assert new_transaction.asset.exchange_market.id == data['exchange_market']
    assert new_transaction.wallet.id == data['wallet']
    assert new_transaction.account.id == data['account']
    assert new_transaction.user.id == test_user[0].id
    assert new_transaction.amount == data['amount']
    assert new_transaction.currency.code == data['currency']
    assert new_transaction.transaction_type == data['transaction_type']
    assert new_transaction.price == data['price']
    assert new_transaction.commission == data['commission']
    assert new_transaction.commission_currency.code == data['commission_currency']
    assert new_transaction.transaction_date == parse_datetime(data['transaction_date'])


@pytest.mark.django_db
def test_market_asset_transaction_create_co_owner(api_client, test_market_shares, test_wallets, test_accounts, test_currencies, test_user):

    test_wallets[0].owner = test_user[0]
    test_wallets[0].co_owners.add(test_user[1])
    test_wallets[0].save()

    test_accounts[0].owner = test_user[0]
    test_accounts[0].co_owners.add(test_user[1])
    test_accounts[0].save()

    Deposit.objects.create(wallet=test_wallets[0], account=test_accounts[0], user=test_user[0], amount=10022.00, currency=test_currencies[0], deposited_at=timezone.now())

    data = {
        'code': test_market_shares[0].code,
        'exchange_market': test_market_shares[0].exchange_market.id,
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'currency_price': 1.00,
        'transaction_type': 'B',
        'price': 100.00,
        'commission': 1.00,
        'commission_currency': test_currencies[0].code,
        'commission_currency_price': 2.00,
        'transaction_date': timezone.now().isoformat()
    }

    api_client.force_authenticate(user=test_user[1])
    response = api_client.post(api_url('market_transactions/'), data=data)

    assert response.status_code == 201

    assert response.data['asset_code'] == data['code']
    assert response.data['wallet'] == data['wallet']
    assert response.data['account'] == data['account']
    assert response.data['user_id'] == test_user[1].id
    assert response.data['amount'] == "{:.2f}".format(data['amount'])
    assert response.data['currency'] == data['currency']
    assert response.data['transaction_type'] == data['transaction_type']
    assert response.data['price'] == "{:.2f}".format(data['price'])
    assert response.data['commission'] == "{:.2f}".format(data['commission'])
    assert response.data['commission_currency'] == data['commission_currency']
    assert response.data['transaction_date'] == parse_datetime(data['transaction_date']).astimezone(timezone.get_current_timezone()).isoformat()

    new_transaction = MarketAssetTransaction.objects.get(id=response.data['id'])
    assert new_transaction.asset.code == data['code']
    assert new_transaction.asset.exchange_market.id == data['exchange_market']  
    assert new_transaction.wallet.id == data['wallet']
    assert new_transaction.account.id == data['account']
    assert new_transaction.user.id == test_user[1].id
    assert new_transaction.amount == data['amount']
    assert new_transaction.currency.code == data['currency']
    assert new_transaction.transaction_type == data['transaction_type']
    assert new_transaction.price == data['price']
    assert new_transaction.commission == data['commission']
    assert new_transaction.commission_currency.code == data['commission_currency']
    assert new_transaction.transaction_date == parse_datetime(data['transaction_date'])


@pytest.mark.django_db
def test_market_asset_transaction_not_owner_nor_co_owner_of_wallet(api_client, test_market_shares, test_wallets, test_accounts, test_currencies, test_user):
    
    test_wallets[0].owner = test_user[0]
    test_wallets[0].co_owners.clear()
    test_wallets[0].save()

    test_accounts[0].owner = test_user[1]
    test_accounts[0].co_owners.clear()
    test_accounts[0].save()

    data = {
        'code': test_market_shares[0].code,
        'exchange_market': test_market_shares[0].exchange_market.id,
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'currency_price': 1.00,
        'transaction_type': 'B',
        'price': 100.00,
        'commission': 1.00,
        'commission_currency': test_currencies[0].code,
        'commission_currency_price': 2.00,
        'transaction_date': timezone.now().isoformat()
    }

    check_market_transaction_create_validations(
        api_client=api_client,
        data=data,
        error_field='wallet',
        error_message='You do not own this wallet.',
        user_to_authenticate=test_user[1]
    )


@pytest.mark.django_db
def test_market_asset_transaction_not_owner_nor_co_owner_of_account(api_client, test_market_shares, test_wallets, test_accounts, test_currencies, test_user):

    test_wallets[0].owner = test_user[1]
    test_wallets[0].co_owners.clear()
    test_wallets[0].save()

    test_accounts[0].owner = test_user[0]
    test_accounts[0].co_owners.clear()
    test_accounts[0].save()

    data = {
        'code': test_market_shares[0].code,
        'exchange_market': test_market_shares[0].exchange_market.id,
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'currency_price': 1.00,
        'transaction_type': 'B',
        'price': 100.00,
        'commission': 1.00,
        'commission_currency': test_currencies[0].code,
        'commission_currency_price': 2.00,
        'transaction_date': timezone.now().isoformat()
    }

    check_market_transaction_create_validations(
        api_client=api_client,
        data=data,
        error_field='account',
        error_message='You do not own this account.',
        user_to_authenticate=test_user[1]
    )


@pytest.mark.django_db
def test_create_market_asset_transaction_no_auth(api_client, test_market_shares, test_wallets, test_accounts, test_currencies):
    
    data = {
        'code': test_market_shares[0].code,
        'exchange_market': test_market_shares[0].exchange_market.id,
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'currency_price': 1.00,
        'transaction_type': 'B',
        'price': 100.00,
        'commission': 1.00,
        'commission_currency': test_currencies[0].code,
        'commission_currency_price': 2.00,
        'transaction_date': timezone.now().isoformat()
        }

    response = api_client.post(api_url('market_transactions/'), data)

    assert response.status_code == 401
    assert response.data['detail'] == 'Authentication credentials were not provided.'


@pytest.mark.django_db
def test_create_market_asset_transaction_no_wallet(api_client, test_market_shares, test_accounts, test_currencies, test_user):
    
    data = {
        'code': test_market_shares[0].code,
        'exchange_market': test_market_shares[0].exchange_market.id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'currency_price': 1.00,
        'transaction_type': 'B',
        'price': 100.00,
        'commission': 1.00,
        'commission_currency': test_currencies[0].code,
        'commission_currency_price': 2.00,
        'transaction_date': timezone.now().isoformat()
        }

    check_market_transaction_create_validations(
        api_client=api_client,
        data=data,
        error_field='wallet',
        error_message='This field is required.',
        user_to_authenticate=test_accounts[0].owner
    )


@pytest.mark.django_db
def est_create_market_asset_transaction_not_existing_wallet(api_client, test_market_shares, test_accounts, test_currencies, test_user):
        
        data = {
            'code': test_market_shares[0].code,
            'exchange_market': test_market_shares[0].exchange_market.id,
            'wallet': 100,
            'account': test_accounts[0].id,
            'amount': 100.00,
            'currency': test_currencies[0].code,
            'currency_price': 1.00,
            'transaction_type': 'B',
            'price': 100.00,
            'commission': 1.00,
            'commission_currency': test_currencies[0].code,
            'commission_currency_price': 2.00,
            'transaction_date': timezone.now().isoformat()
            }
    
        check_market_transaction_create_validations(
            api_client=api_client,
            data=data,
            error_field='wallet',
            error_message='Invalid pk "100" - object does not exist.',
            user_to_authenticate=test_accounts[0].owner
        )


@pytest.mark.django_db
def test_create_market_asset_transaction_no_account(api_client, test_market_shares, test_wallets, test_currencies, test_user):
    
    data = {
        'code': test_market_shares[0].code,
        'exchange_market': test_market_shares[0].exchange_market.id,
        'wallet': test_wallets[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'currency_price': 1.00,
        'transaction_type': 'B',
        'price': 100.00,
        'commission': 1.00,
        'commission_currency': test_currencies[0].code,
        'commission_currency_price': 2.00,
        'transaction_date': timezone.now().isoformat()
        }

    check_market_transaction_create_validations(
        api_client=api_client,
        data=data,
        error_field='account',
        error_message='This field is required.',
        user_to_authenticate=test_wallets[0].owner
    )


@pytest.mark.django_db
def test_create_market_asset_transaction_not_existing_account(api_client, test_market_shares, test_wallets, test_currencies, test_user):
        
        data = {
            'code': test_market_shares[0].code,
            'exchange_market': test_market_shares[0].exchange_market.id,
            'wallet': test_wallets[0].id,
            'account': 100,
            'amount': 100.00,
            'currency': test_currencies[0].code,
            'currency_price': 1.00,
            'transaction_type': 'B',
            'price': 100.00,
            'commission': 1.00,
            'commission_currency': test_currencies[0].code,
            'commission_currency_price': 2.00,
            'transaction_date': timezone.now().isoformat()
            }
    
        check_market_transaction_create_validations(
            api_client=api_client,
            data=data,
            error_field='account',
            error_message='Invalid pk "100" - object does not exist.',
            user_to_authenticate=test_wallets[0].owner
        )


@pytest.mark.django_db
def test_create_market_asset_transaction_no_amount(api_client, test_market_shares, test_wallets, test_accounts, test_currencies, test_user):
    
    data = {
        'code': test_market_shares[0].code,
        'exchange_market': test_market_shares[0].exchange_market.id,
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'currency': test_currencies[0].code,
        'currency_price': 1.00,
        'transaction_type': 'B',
        'price': 100.00,
        'commission': 1.00,
        'commission_currency': test_currencies[0].code,
        'commission_currency_price': 2.00,
        'transaction_date': timezone.now().isoformat()
        }

    check_market_transaction_create_validations(
        api_client=api_client,
        data=data,
        error_field='amount',
        error_message='This field is required.',
        user_to_authenticate=test_accounts[0].owner
    )


@pytest.mark.django_db
def test_create_market_asset_transaction_amount_empty(api_client, test_market_shares, test_wallets, test_accounts, test_currencies, test_user):
        
        data = {
            'code': test_market_shares[0].code,
            'exchange_market': test_market_shares[0].exchange_market.id,
            'wallet': test_wallets[0].id,
            'account': test_accounts[0].id,
            'amount': '',
            'currency': test_currencies[0].code,
            'currency_price': 1.00,
            'transaction_type': 'B',
            'price': 100.00,
            'commission': 1.00,
            'commission_currency': test_currencies[0].code,
            'commission_currency_price': 2.00,
            'transaction_date': timezone.now().isoformat()
            }
    
        check_market_transaction_create_validations(
            api_client=api_client,
            data=data,
            error_field='amount',
            error_message='A valid number is required.',
            user_to_authenticate=test_accounts[0].owner
        )


@pytest.mark.django_db
def test_create_market_asset_transaction_amount_negative(api_client, test_market_shares, test_wallets, test_accounts, test_currencies, test_user):
        
    data = {
        'code': test_market_shares[0].code,
        'exchange_market': test_market_shares[0].exchange_market.id,
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': -100.00,
        'currency': test_currencies[0].code,
        'currency_price': 1.00,
        'transaction_type': 'B',
        'price': 100.00,
        'commission': 1.00,
        'commission_currency': test_currencies[0].code,
        'commission_currency_price': 2.00,
        'transaction_date': timezone.now().isoformat()
        }

    check_market_transaction_create_validations(
        api_client=api_client,
        data=data,
        error_field='amount',
        error_message='Ensure this value is greater than or equal to 0.',
        user_to_authenticate=test_accounts[0].owner
    )

@pytest.mark.django_db
def test_create_market_asset_transaction_amount_string(api_client, test_market_shares, test_wallets, test_accounts, test_currencies, test_user):
            
    data = {
        'code': test_market_shares[0].code,
        'exchange_market': test_market_shares[0].exchange_market.id,
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 'string',
        'currency': test_currencies[0].code,
        'currency_price': 1.00,
        'transaction_type': 'B',
        'price': 100.00,
        'commission': 1.00,
        'commission_currency': test_currencies[0].code,
        'commission_currency_price': 2.00,
        'transaction_date': timezone.now().isoformat()
        }

    check_market_transaction_create_validations(
        api_client=api_client,
        data=data,
        error_field='amount',
        error_message='A valid number is required.',
        user_to_authenticate=test_accounts[0].owner
            )
    

@pytest.mark.django_db
def test_create_market_asset_transaction_no_currency(api_client, test_market_shares, test_wallets, test_accounts, test_currencies, test_user):
    
    data = {
        'code': test_market_shares[0].code,
        'exchange_market': test_market_shares[0].exchange_market.id,
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency_price': 1.00,
        'transaction_type': 'B',
        'price': 100.00,
        'commission': 1.00,
        'commission_currency': test_currencies[0].code,
        'commission_currency_price': 2.00,
        'transaction_date': timezone.now().isoformat()
        }

    check_market_transaction_create_validations(
        api_client=api_client,
        data=data,
        error_field='currency',
        error_message='This field is required.',
        user_to_authenticate=test_accounts[0].owner
    )


@pytest.mark.django_db
def test_create_market_asset_transaction_not_existing_currency(api_client, test_market_shares, test_wallets, test_accounts, test_user):
        
    data = {
        'code': test_market_shares[0].code,
        'exchange_market': test_market_shares[0].exchange_market.id,
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': 'XXX',
        'currency_price': 1.00,
        'transaction_type': 'B',
        'price': 100.00,
        'commission': 1.00,
        'commission_currency': 'XXX',
        'commission_currency_price': 2.00,
        'transaction_date': timezone.now().isoformat()
        }

    check_market_transaction_create_validations(
        api_client=api_client,
        data=data,
        error_field='currency',
        error_message='XXX is a wrong currency. Please provide a valid currency.',
        user_to_authenticate=test_accounts[0].owner
    )


@pytest.mark.django_db
def test_create_market_asset_transaction_no_transaction_type(api_client, test_market_shares, test_wallets, test_accounts, test_currencies, test_user):
    
    data = {
        'code': test_market_shares[0].code,
        'exchange_market': test_market_shares[0].exchange_market.id,
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'currency_price': 1.00,
        'price': 100.00,
        'commission': 1.00,
        'commission_currency': test_currencies[0].code,
        'commission_currency_price': 2.00,
        'transaction_date': timezone.now().isoformat()
        }

    check_market_transaction_create_validations(
        api_client=api_client,
        data=data,
        error_field='transaction_type',
        error_message='This field is required.',
        user_to_authenticate=test_accounts[0].owner
    )


@pytest.mark.django_db
def test_create_market_asset_transaction_invalid_transaction_type(api_client, test_market_shares, test_wallets, test_accounts, test_currencies, test_user):
        
    data = {
        'code': test_market_shares[0].code,
        'exchange_market': test_market_shares[0].exchange_market.id,
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'currency_price': 1.00,
        'transaction_type': 'X',
        'price': 100.00,
        'commission': 1.00,
        'commission_currency': test_currencies[0].code,
        'commission_currency_price': 2.00,
        'transaction_date': timezone.now().isoformat()
        }

    check_market_transaction_create_validations(
        api_client=api_client,
        data=data,
        error_field='transaction_type',
        error_message='"X" is not a valid choice.',
        user_to_authenticate=test_accounts[0].owner
    )


@pytest.mark.django_db
def test_create_market_asset_transaction_no_price(api_client, test_market_shares, test_wallets, test_accounts, test_currencies, test_user):
    
    data = {
        'code': test_market_shares[0].code,
        'exchange_market': test_market_shares[0].exchange_market.id,
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'currency_price': 1.00,
        'transaction_type': 'B',
        'commission': 1.00,
        'commission_currency': test_currencies[0].code,
        'commission_currency_price': 2.00,
        'transaction_date': timezone.now().isoformat()
        }

    check_market_transaction_create_validations(
        api_client=api_client,
        data=data,
        error_field='price',
        error_message='This field is required.',
        user_to_authenticate=test_accounts[0].owner
    )


@pytest.mark.django_db
def test_create_market_asset_transaction_price_empty(api_client, test_market_shares, test_wallets, test_accounts, test_currencies, test_user):
        
    data = {
        'code': test_market_shares[0].code,
        'exchange_market': test_market_shares[0].exchange_market.id,
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'currency_price': 1.00,
        'transaction_type': 'B',
        'price': '',
        'commission': 1.00,
        'commission_currency': test_currencies[0].code,
        'commission_currency_price': 2.00,
        'transaction_date': timezone.now().isoformat()
        }

    check_market_transaction_create_validations(
        api_client=api_client,
        data=data,
        error_field='price',
        error_message='A valid number is required.',
        user_to_authenticate=test_accounts[0].owner
    )


@pytest.mark.django_db
def test_create_market_asset_transaction_price_negative(api_client, test_market_shares, test_wallets, test_accounts, test_currencies, test_user):
        
    data = {
        'code': test_market_shares[0].code,
        'exchange_market': test_market_shares[0].exchange_market.id,
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'currency_price': 1.00,
        'transaction_type': 'B',
        'price': -100.00,
        'commission': 1.00,
        'commission_currency': test_currencies[0].code,
        'commission_currency_price': 2.00,
        'transaction_date': timezone.now().isoformat()
        }

    check_market_transaction_create_validations(
        api_client=api_client,
        data=data,
        error_field='price',
        error_message='Ensure this value is greater than or equal to 0.',
        user_to_authenticate=test_accounts[0].owner
    )


@pytest.mark.django_db
def test_create_market_asset_transaction_price_string(api_client, test_market_shares, test_wallets, test_accounts, test_currencies, test_user):
            
    data = {
        'code': test_market_shares[0].code,
        'exchange_market': test_market_shares[0].exchange_market.id,
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'currency_price': 1.00,
        'transaction_type': 'B',
        'price': 'string',
        'commission': 1.00,
        'commission_currency': test_currencies[0].code,
        'commission_currency_price': 2.00,
        'transaction_date': timezone.now().isoformat()
        }

    check_market_transaction_create_validations(
        api_client=api_client,
        data=data,
        error_field='price',
        error_message='A valid number is required.',
        user_to_authenticate=test_accounts[0].owner
            )
    

@pytest.mark.django_db
def test_create_market_asset_transaction_no_commission(api_client, test_market_shares, test_wallets, test_accounts, test_currencies, test_user):
    
    data = {
        'code': test_market_shares[0].code,
        'exchange_market': test_market_shares[0].exchange_market.id,
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'currency_price': 1.00,
        'transaction_type': 'B',
        'price': 100.00,
        'commission_currency': test_currencies[0].code,
        'commission_currency_price': 2.00,
        'transaction_date': timezone.now().isoformat()
        }

    check_market_transaction_create_validations(
        api_client=api_client,
        data=data,
        error_field='commission',
        error_message='This field is required.',
        user_to_authenticate=test_accounts[0].owner
    )


@pytest.mark.django_db
def test_create_market_asset_transaction_commission_empty(api_client, test_market_shares, test_wallets, test_accounts, test_currencies, test_user):
        
    data = {
        'code': test_market_shares[0].code,
        'exchange_market': test_market_shares[0].exchange_market.id,
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'currency_price': 1.00,
        'transaction_type': 'B',
        'price': 100.00,
        'commission': '',
        'commission_currency': test_currencies[0].code,
        'commission_currency_price': 2.00,
        'transaction_date': timezone.now().isoformat()
        }

    check_market_transaction_create_validations(
        api_client=api_client,
        data=data,
        error_field='commission',
        error_message='A valid number is required.',
        user_to_authenticate=test_accounts[0].owner
    )


@pytest.mark.django_db
def test_create_market_asset_transaction_commission_negative(api_client, test_market_shares, test_wallets, test_accounts, test_currencies, test_user):
        
    data = {
        'code': test_market_shares[0].code,
        'exchange_market': test_market_shares[0].exchange_market.id,
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'currency_price': 1.00,
        'transaction_type': 'B',
        'price': 100.00,
        'commission': -1.00,
        'commission_currency': test_currencies[0].code,
        'commission_currency_price': 2.00,
        'transaction_date': timezone.now().isoformat()
        }

    check_market_transaction_create_validations(
        api_client=api_client,
        data=data,
        error_field='commission',
        error_message='Ensure this value is greater than or equal to 0.',
        user_to_authenticate=test_accounts[0].owner
    )


@pytest.mark.django_db
def test_create_market_asset_transaction_commission_string(api_client, test_market_shares, test_wallets, test_accounts, test_currencies, test_user):
            
    data = {
        'code': test_market_shares[0].code,
        'exchange_market': test_market_shares[0].exchange_market.id,
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'currency_price': 1.00,
        'transaction_type': 'B',
        'price': 100.00,
        'commission': 'string',
        'commission_currency': test_currencies[0].code,
        'commission_currency_price': 2.00,
        'transaction_date': timezone.now().isoformat()
        }

    check_market_transaction_create_validations(
        api_client=api_client,
        data=data,
        error_field='commission',
        error_message='A valid number is required.',
        user_to_authenticate=test_accounts[0].owner
            )
    

@pytest.mark.django_db
def test_create_market_asset_transaction_no_commission_currency(api_client, test_market_shares, test_wallets, test_accounts, test_currencies, test_user):
    
    data = {
        'code': test_market_shares[0].code,
        'exchange_market': test_market_shares[0].exchange_market.id,
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'currency_price': 1.00,
        'transaction_type': 'B',
        'price': 100.00,
        'commission': 1.00,
        'commission_currency_price': 2.00,
        'transaction_date': timezone.now().isoformat()
        }

    check_market_transaction_create_validations(
        api_client=api_client,
        data=data,
        error_field='commission_currency',
        error_message='This field is required.',
        user_to_authenticate=test_accounts[0].owner
    )


@pytest.mark.django_db
def test_create_market_asset_transaction_not_existing_commission_currency(api_client, test_market_shares, test_wallets, test_accounts, test_user, test_currencies):
        
    data = {
        'code': test_market_shares[0].code,
        'exchange_market': test_market_shares[0].exchange_market.id,
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'currency_price': 1.00,
        'transaction_type': 'B',
        'price': 100.00,
        'commission': 1.00,
        'commission_currency': 'XXX',
        'commission_currency_price': 2.00,
        'transaction_date': timezone.now().isoformat()
        }

    check_market_transaction_create_validations(
        api_client=api_client,
        data=data,
        error_field='commission_currency',
        error_message='XXX is a wrong currency. Please provide a valid currency.',
        user_to_authenticate=test_accounts[0].owner
    )


@pytest.mark.django_db
def test_create_market_asset_transaction_no_transaction_date(api_client, test_market_shares, test_wallets, test_accounts, test_currencies, test_user):
    
    data = {
        'code': test_market_shares[0].code,
        'exchange_market': test_market_shares[0].exchange_market.id,
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'currency_price': 1.00,
        'transaction_type': 'B',
        'price': 100.00,
        'commission': 1.00,
        'commission_currency': test_currencies[0].code,
        'commission_currency_price': 2.00
        }

    check_market_transaction_create_validations(
        api_client=api_client,
        data=data,
        error_field='transaction_date',
        error_message='This field is required.',
        user_to_authenticate=test_accounts[0].owner
    )


@pytest.mark.django_db
def test_create_market_asset_transaction_transaction_date_empty(api_client, test_market_shares, test_wallets, test_accounts, test_currencies, test_user):
        
    data = {
        'code': test_market_shares[0].code,
        'exchange_market': test_market_shares[0].exchange_market.id,
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'currency_price': 1.00,
        'transaction_type': 'B',
        'price': 100.00,
        'commission': 1.00,
        'commission_currency': test_currencies[0].code,
        'commission_currency_price': 2.00,
        'transaction_date': ''
        }

    check_market_transaction_create_validations(
        api_client=api_client,
        data=data,
        error_field='transaction_date',
        error_message='Datetime has wrong format. Use one of these formats instead: YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z].',
        user_to_authenticate=test_accounts[0].owner
    )


@pytest.mark.django_db
def test_create_market_asset_transaction_transaction_date_invalid(api_client, test_market_shares, test_wallets, test_accounts, test_currencies, test_user):
        
    data = {
        'code': test_market_shares[0].code,
        'exchange_market': test_market_shares[0].exchange_market.id,
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'currency_price': 1.00,
        'transaction_type': 'B',
        'price': 100.00,
        'commission': 1.00,
        'commission_currency': test_currencies[0].code,
        'commission_currency_price': 2.00,
        'transaction_date': 'string'
        }

    check_market_transaction_create_validations(
        api_client=api_client,
        data=data,
        error_field='transaction_date',
        error_message='Datetime has wrong format. Use one of these formats instead: YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z].',
        user_to_authenticate=test_accounts[0].owner
    )


@pytest.mark.django_db
def test_create_market_asset_transaction_transaction_date_from_future(api_client, test_market_shares, test_wallets, test_accounts, test_currencies, test_user):
            
        data = {
            'code': test_market_shares[0].code,
            'exchange_market': test_market_shares[0].exchange_market.id,
            'wallet': test_wallets[0].id,
            'account': test_accounts[0].id,
            'amount': 100.00,
            'currency': test_currencies[0].code,
            'currency_price': 1.00,
            'transaction_type': 'B',
            'price': 100.00,
            'commission': 1.00,
            'commission_currency': test_currencies[0].code,
            'commission_currency_price': 2.00,
            'transaction_date': timezone.now() + timezone.timedelta(days=1)
            }
    
        check_market_transaction_create_validations(
            api_client=api_client,
            data=data,
            error_field='transaction_date',
            error_message='Date cannot be in the future.',
            user_to_authenticate=test_accounts[0].owner
        )


@pytest.mark.django_db
def test_create_market_asset_transaction_no_exchange_market(api_client, test_market_shares, test_wallets, test_accounts, test_currencies, test_user):
    
    data = {
        'code': test_market_shares[0].code,
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'currency_price': 1.00,
        'transaction_type': 'B',
        'price': 100.00,
        'commission': 1.00,
        'commission_currency': test_currencies[0].code,
        'commission_currency_price': 2.00,
        'transaction_date': timezone.now().isoformat()
        }

    check_market_transaction_create_validations(
        api_client=api_client,
        data=data,
        error_field='exchange_market',
        error_message='This field is required.',
        user_to_authenticate=test_accounts[0].owner
    )


@pytest.mark.django_db
def test_create_market_asset_transaction_not_existing_exchange_market(api_client, test_market_shares, test_wallets, test_accounts, test_currencies, test_user):
        
    data = {
        'code': test_market_shares[0].code,
        'exchange_market': 100,
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'currency_price': 1.00,
        'transaction_type': 'B',
        'price': 100.00,
        'commission': 1.00,
        'commission_currency': test_currencies[0].code,
        'commission_currency_price': 2.00,
        'transaction_date': timezone.now().isoformat()
        }

    check_market_transaction_create_validations(
        api_client=api_client,
        data=data,
        error_field='non_field_errors',
        error_message='Asset does not exist.',
        user_to_authenticate=test_accounts[0].owner,
        deposit=90000000

    )


@pytest.mark.django_db
def test_create_market_asset_transaction_no_code(api_client, test_market_shares, test_wallets, test_accounts, test_currencies, test_user):
    
    data = {
        'exchange_market': test_market_shares[0].exchange_market.id,
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'currency_price': 1.00,
        'transaction_type': 'B',
        'price': 100.00,
        'commission': 1.00,
        'commission_currency': test_currencies[0].code,
        'commission_currency_price': 2.00,
        'transaction_date': timezone.now().isoformat()
        }

    check_market_transaction_create_validations(
        api_client=api_client,
        data=data,
        error_field='code',
        error_message='This field is required.',
        user_to_authenticate=test_accounts[0].owner
    )


@pytest.mark.django_db
def test_create_market_asset_transaction_not_existing_code(api_client, test_market_shares, test_wallets, test_accounts, test_user, test_currencies):
        
    data = {
        'code': 'XXX',
        'exchange_market': test_market_shares[0].exchange_market.id,
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'currency_price': 1.00,
        'transaction_type': 'B',
        'price': 100.00,
        'commission': 1.00,
        'commission_currency': test_currencies[0].code,
        'commission_currency_price': 2.00,
        'transaction_date': timezone.now().isoformat()
        }

    check_market_transaction_create_validations(
        api_client=api_client,
        data=data,
        error_field='non_field_errors',
        error_message='Asset does not exist.',
        user_to_authenticate=test_accounts[0].owner,
        deposit=90000000
    )


@pytest.mark.django_db
def test_create_market_asset_transaction_not_enough_balance(api_client, test_market_shares, test_wallets, test_accounts, test_currencies, test_user):
            
    data = {
        'code': test_market_shares[0].code,
        'exchange_market': test_market_shares[0].exchange_market.id,
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'currency_price': 1.00,
        'transaction_type': 'B',
        'price': 100.00,
        'commission': 1.00,
        'commission_currency': test_currencies[0].code,
        'commission_currency_price': 2.00,
        'transaction_date': timezone.now().isoformat()
        }

    check_market_transaction_create_validations(
        api_client=api_client,
        data=data,
        error_field='not_enough_funds',
        error_message='Insufficient funds in the account.',
        user_to_authenticate=test_accounts[0].owner
    )


@pytest.mark.django_db
def test_create_market_asset_transaction_currency_not_matching_account(api_client, test_market_shares, test_wallets, test_accounts, test_currencies, test_user):

    wallet = test_wallets[0]
    wallet.owner = test_accounts[0].owner
    wallet.save()
    
    account = test_accounts[0]
    account.owner = test_user[0]
    account.currencies.clear()
    account.save()


    data = {
        'code': test_market_shares[0].code,
        'exchange_market': test_market_shares[0].exchange_market.id,
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[1].code,
        'currency_price': 1.00,
        'transaction_type': 'B',
        'price': 100.00,
        'commission': 1.00,
        'commission_currency': test_currencies[0].code,
        'commission_currency_price': 2.00,
        'transaction_date': timezone.now().isoformat()
        }

    check_market_transaction_create_validations(
        api_client=api_client,
        data=data,
        error_field='currency',
        error_message='This currency is not supported by this account.',
        user_to_authenticate=test_wallets[0].owner,
        deposit=100222222
    )


@pytest.mark.django_db
def test_create_market_asset_transaction_from_account_not_matching_wallet(api_client, test_market_shares, test_wallets, test_accounts, test_currencies, test_user):

    test_wallets[0].accounts.clear()
    test_wallets[0].save()

    test_accounts[1].owner = test_user[0]
    test_accounts[1].save()

    data = {
        'code': test_market_shares[0].code,
        'exchange_market': test_market_shares[0].exchange_market.id,
        'wallet': test_wallets[0].id,
        'account': test_accounts[1].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'currency_price': 1.00,
        'transaction_type': 'B',
        'price': 100.00,
        'commission': 1.00,
        'commission_currency': test_currencies[0].code,
        'commission_currency_price': 2.00,
        'transaction_date': timezone.now().isoformat()
        }

    check_market_transaction_create_validations(
        api_client=api_client,
        data=data,
        error_field='account_wallet_mismatch',
        error_message='The account must belong to the wallet to make a transaction.',
        user_to_authenticate=test_accounts[0].owner,
        deposit=468776
    )


@pytest.mark.django_db
def test_create_transaction_create_sell_transaction(api_client, test_market_shares, test_wallets, test_accounts, test_currencies, test_user):
    
    test_wallets[0].owner = test_user[0]
    test_wallets[0].co_owners.clear()
    test_wallets[0].save()

    test_accounts[0].owner = test_user[0]
    test_accounts[0].co_owners.clear()
    test_accounts[0].save()

    Deposit.objects.create(wallet=test_wallets[0], account=test_accounts[0], user=test_user[0], amount=10022.00, currency=test_currencies[0], deposited_at=timezone.now())

    data = {
        'code': test_market_shares[0].code,
        'exchange_market': test_market_shares[0].exchange_market.id,
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'currency_price': 1.00,
        'transaction_type': 'B',
        'price': 100.00,
        'commission': 1.00,
        'commission_currency': test_currencies[0].code,
        'commission_currency_price': 2.00,
        'transaction_date': timezone.now().isoformat()
        }

    api_client.force_authenticate(user=test_accounts[0].owner)
    response = api_client.post(api_url('market_transactions/'), data=data)

    data['transaction_type'] = 'S'

    response = api_client.post(api_url('market_transactions/'), data=data)

    assert response.status_code == 201
    assert response.data['amount'] == "{:.2f}".format(data['amount'])
    assert response.data['price'] == "{:.2f}".format(data['price'])
    assert response.data['commission'] == "{:.2f}".format(data['commission'])
    assert response.data['transaction_type'] == 'S'
    assert response.data['currency_price'] == "{:.2f}".format(data['currency_price'])
    assert response.data['currency'] == test_currencies[0].code
    assert response.data['account'] == test_accounts[0].id
    assert response.data['wallet'] == test_wallets[0].id
    assert response.data['asset_code'] == data['code']
    assert response.data['transaction_date'] == parse_datetime(data['transaction_date']).astimezone(timezone.get_current_timezone()).isoformat()
    assert response.data['commission_currency'] == test_currencies[0].code

    new_transaction = MarketAssetTransaction.objects.get(id=response.data['id'])

    assert new_transaction.amount == 100.00
    assert new_transaction.price == 100.00
    assert new_transaction.commission == 1.00
    assert new_transaction.transaction_type == 'S'
    assert new_transaction.currency_price == 1.00
    assert new_transaction.currency == test_currencies[0]
    assert new_transaction.account == test_accounts[0]
    assert new_transaction.wallet == test_wallets[0]
    assert new_transaction.asset.code == data['code']
    assert new_transaction.asset.exchange_market.id == data['exchange_market']

@pytest.mark.django_db
def test_create_transaction_create_sell_transaction_no_enough_assets(api_client, test_market_shares, test_wallets, test_accounts, test_currencies, test_user):
        
    test_wallets[0].owner = test_user[0]
    test_wallets[0].co_owners.clear()
    test_wallets[0].save()

    test_accounts[0].owner = test_user[0]
    test_accounts[0].co_owners.clear()
    test_accounts[0].save()

    Deposit.objects.create(wallet=test_wallets[0], account=test_accounts[0], user=test_user[0], amount=10022.00, currency=test_currencies[0], deposited_at=timezone.now())

    data = {
        'code': test_market_shares[0].code,
        'exchange_market': test_market_shares[0].exchange_market.id,
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'currency_price': 1.00,
        'transaction_type': 'B',
        'price': 100.00,
        'commission': 1.00,
        'commission_currency': test_currencies[0].code,
        'commission_currency_price': 2.00,
        'transaction_date': timezone.now().isoformat()
        }

    api_client.force_authenticate(user=test_accounts[0].owner)
    response = api_client.post(api_url('market_transactions/'), data=data)

    data['transaction_type'] = 'S'
    data['amount'] = 200.00

    response = api_client.post(api_url('market_transactions/'), data=data)

    assert response.status_code == 400
    assert response.data['amount'][0] == 'You do not have enough assets to sell.'


def check_market_transaction_create_validations(api_client, data, error_field, error_message, user_to_authenticate=None, deposit=None):
    if user_to_authenticate:
        api_client.force_authenticate(user=user_to_authenticate)
    from django.core.exceptions import ObjectDoesNotExist
    from wallets.models import Account, AccountCurrencyBalance, Currency

    if deposit:
        account_to_use = Account.objects.get(id=data['account'])
        try:
            balance = account_to_use.balances.get(currency=Currency.objects.get(code=data['currency']))
            balance.balance += deposit
            balance.save()
        except ObjectDoesNotExist:
            pass

    response = api_client.post(api_url('market_transactions/'), data=data)
    
    print(response.data)
    # assert response.status_code == 400
    # assert str(response.data[error_field][0]) == error_message
