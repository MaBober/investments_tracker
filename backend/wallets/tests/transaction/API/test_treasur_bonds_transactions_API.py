import pytest

from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from wallets.models import TreasuryBondsTransaction, Deposit, Wallet, Account, Currency

from wallets.tests.test_fixture import test_user, authenticated_client, api_client, admin_logged_client, api_url, test_currencies, test_countries
from wallets.tests.account.test_fixture import test_accounts, test_account_types, test_account_institution_types, test_institution
from wallets.tests.asset.test_fixture import test_asset_types, test_exchange_marketes, test_market_shares, test_treasury_bonds
from wallets.tests.wallet.test_fixture import test_wallets
from wallets.tests.deposit.test_fixture import test_deposits
from wallets.tests.transaction.test_fixture import test_market_asset_transactions, test_treasury_bonds_transactions

@pytest.mark.django_db
def test_get_treasury_bonds_transactions(admin_logged_client, test_treasury_bonds_transactions):
    
    response = admin_logged_client.get(api_url('treasury_bond_transactions/'))

    assert response.status_code == 200
    assert response.data['count'] == len(test_treasury_bonds_transactions)

    assert response.data['results'][0]['id'] == test_treasury_bonds_transactions[0].id
    assert response.data['results'][0]['amount'] == "{:.2f}".format(test_treasury_bonds_transactions[0].amount)
    assert response.data['results'][0]['price'] == "{:.2f}".format(test_treasury_bonds_transactions[0].price)
    assert response.data['results'][0]['commission'] == "{:.2f}".format(test_treasury_bonds_transactions[0].commission)
    assert response.data['results'][0]['commission_currency'] == test_treasury_bonds_transactions[0].commission_currency.code
    assert response.data['results'][0]['transaction_type'] == test_treasury_bonds_transactions[0].transaction_type
    assert response.data['results'][0]['transaction_date'] == test_treasury_bonds_transactions[0].transaction_date.astimezone(timezone.get_current_timezone()).isoformat()
    assert response.data['results'][0]['wallet_id'] == test_treasury_bonds_transactions[0].wallet.id
    assert response.data['results'][0]['wallet_id'] == test_treasury_bonds_transactions[0].account.id
    assert response.data['results'][0]['user_id'] == test_treasury_bonds_transactions[0].user.id
    assert response.data['results'][0]['currency'] == test_treasury_bonds_transactions[0].currency.code
    assert response.data['results'][0]['bond'] == test_treasury_bonds_transactions[0].bond.id


@pytest.mark.django_db
def test_get_treasury_bonds_transactions_no_auth(api_client):
    
    response = api_client.get(api_url('treasury_bond_transactions/'))

    assert response.status_code == 401
    assert response.data['detail'] == "Authentication credentials were not provided."


@pytest.mark.django_db
def test_get_treasury_bonds_transactions_no_admin_auth(authenticated_client):
    
    response = authenticated_client.get(api_url('treasury_bond_transactions/'))

    assert response.status_code == 403
    assert response.data['detail'] == "You do not have permission to perform this action."


@pytest.mark.django_db
def test_get_treasury_bonds_transaction_owner(api_client, test_treasury_bonds_transactions):
    
    api_client.force_authenticate(user=test_treasury_bonds_transactions[0].user)
    response = api_client.get(api_url('treasury_bond_transactions/{}/'.format(test_treasury_bonds_transactions[0].id)))

    assert response.status_code == 200

    assert response.data['id'] == test_treasury_bonds_transactions[0].id
    assert response.data['amount'] == "{:.2f}".format(test_treasury_bonds_transactions[0].amount)
    assert response.data['price'] == "{:.2f}".format(test_treasury_bonds_transactions[0].price)
    assert response.data['commission'] == "{:.2f}".format(test_treasury_bonds_transactions[0].commission)
    assert response.data['commission_currency'] == test_treasury_bonds_transactions[0].commission_currency.code
    assert response.data['transaction_type'] == test_treasury_bonds_transactions[0].transaction_type
    assert response.data['transaction_date'] == test_treasury_bonds_transactions[0].transaction_date.astimezone(timezone.get_current_timezone()).isoformat()
    assert response.data['wallet_id'] == test_treasury_bonds_transactions[0].wallet.id
    assert response.data['wallet_id'] == test_treasury_bonds_transactions[0].account.id
    assert response.data['user_id'] == test_treasury_bonds_transactions[0].user.id
    assert response.data['currency'] == test_treasury_bonds_transactions[0].currency.code
    assert response.data['bond'] == test_treasury_bonds_transactions[0].bond.id


@pytest.mark.django_db
def test_get_treasury_bonds_transaction_no_auth(api_client, test_treasury_bonds_transactions):
    
    response = api_client.get(api_url('treasury_bond_transactions/{}/'.format(test_treasury_bonds_transactions[0].id)))

    assert response.status_code == 401
    assert response.data['detail'] == "Authentication credentials were not provided."


@pytest.mark.django_db
def test_get_treasury_bonds_transaction_no_creator(api_client, test_treasury_bonds_transactions, test_user):


    api_client.force_authenticate(user=test_user[1])
    response = api_client.get(api_url('treasury_bond_transactions/{}/'.format(test_treasury_bonds_transactions[0].id)))

    assert response.status_code == 403
    assert response.data['detail'] == "You do not have permission to perform this action."


@pytest.mark.django_db
def test_get_treasury_bonds_transaction_not_found(admin_logged_client, test_treasury_bonds_transactions):
    
    response = admin_logged_client.get(api_url('treasury_bond_transactions/{}/'.format(100)))

    assert response.status_code == 404
    assert response.data['detail'] == 'No TreasuryBondsTransaction matches the given query.'


@pytest.mark.django_db
def test_post_treasury_bonds_transaction_owner(api_client, test_user, test_treasury_bonds, test_accounts, test_wallets, test_currencies):
   
    test_wallets[0].owner = test_user[0]
    test_wallets[0].co_owners.clear()
    test_wallets[0].save()

    test_accounts[0].owner = test_user[0]
    test_accounts[0].co_owners.clear()
    test_accounts[0].save()

    Deposit.objects.create(wallet=test_wallets[0], account=test_accounts[0], user=test_user[0], amount=10022.00, currency=test_currencies[0], deposited_at=timezone.now())

    data = {
        'bond': test_treasury_bonds[0].code,
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'currency_price': 1.0,
        'transaction_type': 'B',
        'price': 100.00,
        'commission': 1.00,
        'commission_currency': test_currencies[0].code,
        'transaction_date': timezone.now()
    }

    api_client.force_authenticate(user=test_user[0])
    response = api_client.post(api_url('treasury_bond_transactions/'), data=data)

    assert response.status_code == 201

    assert response.data['amount'] == "{:.2f}".format(data['amount'])
    assert response.data['price'] == "{:.2f}".format(data['price'])
    assert response.data['commission'] == "{:.2f}".format(data['commission'])
    assert response.data['commission_currency'] == data['commission_currency']
    assert response.data['transaction_type'] == data['transaction_type']
    assert response.data['transaction_date'] == data['transaction_date'].astimezone(timezone.get_current_timezone()).isoformat()
    assert response.data['wallet'] == data['wallet']
    assert response.data['wallet'] == data['account']
    assert response.data['user_id'] == test_user[0].id
    assert response.data['currency'] == data['currency']
    assert response.data['bond'] == data['bond']

    new_transaction = TreasuryBondsTransaction.objects.get(id=response.data['id'])
    assert new_transaction.amount == data['amount']
    assert new_transaction.price == data['price']
    assert new_transaction.commission == data['commission']
    assert new_transaction.commission_currency.code == data['commission_currency']
    assert new_transaction.transaction_type == data['transaction_type']
    assert new_transaction.transaction_date == data['transaction_date']
    assert new_transaction.wallet.id == data['wallet']
    assert new_transaction.account.id == data['account']
    assert new_transaction.user.id == test_user[0].id
    assert new_transaction.currency.code == data['currency']
    assert new_transaction.bond.code == data['bond']


@pytest.mark.django_db
def test_post_treasury_bonds_transaction_co_owner(api_client, test_user, test_treasury_bonds, test_accounts, test_wallets, test_currencies):
   
    test_wallets[0].owner = test_user[0]
    test_wallets[0].co_owners.clear()
    test_wallets[0].co_owners.add(test_user[1])
    test_wallets[0].save()

    test_accounts[0].owner = test_user[0]
    test_accounts[0].co_owners.clear()
    test_accounts[0].co_owners.add(test_user[1])
    test_accounts[0].save()

    Deposit.objects.create(wallet=test_wallets[0], account=test_accounts[0], user=test_user[0], amount=10022.00, currency=test_currencies[0], deposited_at=timezone.now())

    data = {
        'bond': test_treasury_bonds[0].code,
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'currency_price': 1.0,
        'transaction_type': 'B',
        'price': 100.00,
        'commission': 1.00,
        'commission_currency': test_currencies[0].code,
        'transaction_date': timezone.now()
    }

    api_client.force_authenticate(user=test_user[1])
    response = api_client.post(api_url('treasury_bond_transactions/'), data=data)

    assert response.status_code == 201

    assert response.data['amount'] == "{:.2f}".format(data['amount'])
    assert response.data['price'] == "{:.2f}".format(data['price'])
    assert response.data['commission'] == "{:.2f}".format(data['commission'])
    assert response.data['commission_currency'] == data['commission_currency']
    assert response.data['transaction_type'] == data['transaction_type']
    assert response.data['transaction_date'] == data['transaction_date'].astimezone(timezone.get_current_timezone()).isoformat()
    assert response.data['wallet'] == data['wallet']
    assert response.data['wallet'] == data['account']
    assert response.data['user_id'] == test_user[1].id
    assert response.data['currency'] == data['currency']
    assert response.data['bond'] == data['bond']

    new_transaction = TreasuryBondsTransaction.objects.get(id=response.data['id'])
    assert new_transaction.amount == data['amount']
    assert new_transaction.price == data['price']
    assert new_transaction.commission == data['commission']
    assert new_transaction.commission_currency.code == data['commission_currency']
    assert new_transaction.transaction_type == data['transaction_type']
    assert new_transaction.transaction_date == data['transaction_date']
    assert new_transaction.wallet.id == data['wallet']
    assert new_transaction.account.id == data['account']
    assert new_transaction.user.id == test_user[1].id
    assert new_transaction.currency.code == data['currency']
    assert new_transaction.bond.code == data['bond']


@pytest.mark.django_db
def test_market_asset_transaction_not_owner_nor_co_owner_of_wallet(api_client, test_user, test_treasury_bonds, test_accounts, test_wallets, test_currencies):
   
    test_wallets[0].owner = test_user[0]
    test_wallets[0].co_owners.clear()
    test_wallets[0].save()

    test_accounts[0].owner = test_user[0]
    test_accounts[0].co_owners.clear()
    test_accounts[0].save()

    Deposit.objects.create(wallet=test_wallets[0], account=test_accounts[0], user=test_user[0], amount=10022.00, currency=test_currencies[0], deposited_at=timezone.now())

    data = {
        'bond': test_treasury_bonds[0].code,
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'currency_price': 1.0,
        'transaction_type': 'B',
        'price': 100.00,
        'commission': 1.00,
        'commission_currency': test_currencies[0].code,
        'transaction_date': timezone.now()
    }

    check_treasury_bonds_transaction_bonds_validations(
        api_client=api_client,
        data=data,
        error_field='wallet',
        error_message='You do not own this wallet.',
        user_to_authenticate=test_user[1]
    
    )


@pytest.mark.django_db
def test_market_asset_transaction_not_owner_nor_co_owner_of_account(api_client, test_user, test_treasury_bonds, test_accounts, test_wallets, test_currencies):
   
    test_wallets[0].owner = test_user[0]
    test_wallets[0].co_owners.clear()
    test_wallets[0].save()

    test_accounts[0].owner = test_user[0]
    test_accounts[0].co_owners.clear()
    test_accounts[0].save()

    Deposit.objects.create(wallet=test_wallets[0], account=test_accounts[0], user=test_user[0], amount=10022.00, currency=test_currencies[0], deposited_at=timezone.now())

    data = {
        'bond': test_treasury_bonds[0].code,
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'currency_price': 1.0,
        'transaction_type': 'B',
        'price': 100.00,
        'commission': 1.00,
        'commission_currency': test_currencies[0].code,
        'transaction_date': timezone.now()
    }

    check_treasury_bonds_transaction_bonds_validations(
        api_client=api_client,
        data=data,
        error_field='account',
        error_message='You do not own this account.',
        user_to_authenticate=test_user[1]
    
    )


@pytest.mark.django_db
def test_market_asset_transaction_no_auth(api_client, test_user, test_treasury_bonds, test_accounts, test_wallets, test_currencies):
       

    data = {
        'bond': test_treasury_bonds[0].code,
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'currency_price': 1.0,
        'transaction_type': 'B',
        'price': 100.00,
        'commission': 1.00,
        'commission_currency': test_currencies[0].code,
        'transaction_date': timezone.now()
    }

    response = api_client.post(api_url('treasury_bond_transactions/'), data=data)

    assert response.status_code == 401
    assert response.data['detail'] == "Authentication credentials were not provided."


@pytest.mark.django_db
def test_market_asset_transaction_no_bond(api_client, test_user, test_treasury_bonds, test_accounts, test_wallets, test_currencies):

    test_wallets[0].owner = test_user[0]
    test_wallets[0].co_owners.clear()
    test_wallets[0].save()

    test_accounts[0].owner = test_user[0]
    test_accounts[0].co_owners.clear()
    test_accounts[0].save()

    Deposit.objects.create(wallet=test_wallets[0], account=test_accounts[0], user=test_user[0], amount=10022.00, currency=test_currencies[0], deposited_at=timezone.now())

    data = {
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'currency_price': 1.0,
        'transaction_type': 'B',
        'price': 100.00,
        'commission': 1.00,
        'commission_currency': test_currencies[0].code,
        'transaction_date': timezone.now()
    }

    check_treasury_bonds_transaction_bonds_validations(
        api_client=api_client,
        data=data,
        error_field='bond',
        error_message='This field is required.',
        user_to_authenticate=test_user[0]
    
    )


@pytest.mark.django_db
def test_market_asset_transaction_not_exisitng_bond(api_client, test_user, test_treasury_bonds, test_accounts, test_wallets, test_currencies):

    test_wallets[0].owner = test_user[0]
    test_wallets[0].co_owners.clear()
    test_wallets[0].save()

    test_accounts[0].owner = test_user[0]
    test_accounts[0].co_owners.clear()
    test_accounts[0].save()

    Deposit.objects.create(wallet=test_wallets[0], account=test_accounts[0], user=test_user[0], amount=10022.00, currency=test_currencies[0], deposited_at=timezone.now())

    data = {
        'bond': 'INVALID',
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'currency_price': 1.0,
        'transaction_type': 'B',
        'price': 100.00,
        'commission': 1.00,
        'commission_currency': test_currencies[0].code,
        'transaction_date': timezone.now()
    }

    check_treasury_bonds_transaction_bonds_validations(
        api_client=api_client,
        data=data,
        error_field='bond',
        error_message='INVALID is a wrong bond. Please provide a valid bond.',
        user_to_authenticate=test_user[0]
    
    )


@pytest.mark.django_db
def test_market_asset_transaction_not_enough_balance(api_client, test_user, test_treasury_bonds, test_accounts, test_wallets, test_currencies):

    test_wallets[0].owner = test_user[0]
    test_wallets[0].co_owners.clear()
    test_wallets[0].save()

    test_accounts[0].owner = test_user[0]
    test_accounts[0].co_owners.clear()
    test_accounts[0].save()

    data = {
        'bond': test_treasury_bonds[0].code,
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'currency_price': 1.0,
        'transaction_type': 'B',
        'price': 100.00,
        'commission': 1.00,
        'commission_currency': test_currencies[0].code,
        'transaction_date': timezone.now()
    }

    check_treasury_bonds_transaction_bonds_validations(
        api_client=api_client,
        data=data,
        error_field='not_enough_funds',
        error_message='Insufficient funds in the account.',
        user_to_authenticate=test_user[0]
    
    )


@pytest.mark.django_db
def test_market_asset_transaction_create_sell_transaction(api_client, test_user, test_treasury_bonds, test_accounts, test_wallets, test_currencies):
    
    test_wallets[0].owner = test_user[0]
    test_wallets[0].co_owners.clear()
    test_wallets[0].save()

    test_accounts[0].owner = test_user[0]
    test_accounts[0].co_owners.clear()
    test_accounts[0].save()

    Deposit.objects.create(wallet=test_wallets[0], account=test_accounts[0], user=test_user[0], amount=10022.00, currency=test_currencies[0], deposited_at=timezone.now())

    data = {
        'bond': test_treasury_bonds[0].code,
        'wallet': test_wallets[0].id,
        'account': test_accounts[0].id,
        'amount': 100.00,
        'currency': test_currencies[0].code,
        'currency_price': 1.0,
        'transaction_type': 'B',
        'price': 100.00,
        'commission': 1.00,
        'commission_currency': test_currencies[0].code,
        'transaction_date': timezone.now()
    }

    api_client.force_authenticate(user=test_user[0])
    response = api_client.post(api_url('treasury_bond_transactions/'), data=data)

    data['transaction_type'] = 'S'

    response = api_client.post(api_url('treasury_bond_transactions/'), data=data)

    assert response.status_code == 201

    assert response.data['amount'] == "{:.2f}".format(data['amount'])
    assert response.data['price'] == "{:.2f}".format(data['price'])
    assert response.data['commission'] == "{:.2f}".format(data['commission'])
    assert response.data['commission_currency'] == data['commission_currency']
    assert response.data['transaction_type'] == data['transaction_type']
    assert response.data['transaction_date'] == data['transaction_date'].astimezone(timezone.get_current_timezone()).isoformat()
    assert response.data['wallet'] == data['wallet']
    assert response.data['wallet'] == data['account']
    assert response.data['user_id'] == test_user[0].id
    assert response.data['currency'] == data['currency']
    assert response.data['bond'] == data['bond']

    new_transaction = TreasuryBondsTransaction.objects.get(id=response.data['id'])
    assert new_transaction.amount == data['amount']
    assert new_transaction.price == data['price']
    assert new_transaction.commission == data['commission']
    assert new_transaction.commission_currency


@pytest.mark.django_db
def test_market_asset_transaction_create_sell_transaction_not_enough_bonds(api_client, test_user, test_treasury_bonds, test_accounts, test_wallets, test_currencies):
            
        test_wallets[0].owner = test_user[0]
        test_wallets[0].co_owners.clear()
        test_wallets[0].save()
    
        test_accounts[0].owner = test_user[0]
        test_accounts[0].co_owners.clear()
        test_accounts[0].save()
    
        Deposit.objects.create(wallet=test_wallets[0], account=test_accounts[0], user=test_user[0], amount=10022.00, currency=test_currencies[0], deposited_at=timezone.now())
    
        data = {
            'bond': test_treasury_bonds[0].code,
            'wallet': test_wallets[0].id,
            'account': test_accounts[0].id,
            'amount': 100.00,
            'currency': test_currencies[0].code,
            'currency_price': 1.0,
            'transaction_type': 'B',
            'price': 100.00,
            'commission': 1.00,
            'commission_currency': test_currencies[0].code,
            'transaction_date': timezone.now()
        }
    
        api_client.force_authenticate(user=test_user[0])
        response = api_client.post(api_url('treasury_bond_transactions/'), data=data)

        data['transaction_type'] = 'S'
        data['amount'] = 200.00

        response = api_client.post(api_url('treasury_bond_transactions/'), data=data)

        check_treasury_bonds_transaction_bonds_validations(
            api_client=api_client,
            data=data,
            error_field='amount',
            error_message='You do not have enough bonds to sell.',
            user_to_authenticate=test_user[0]
        )
    
def check_treasury_bonds_transaction_bonds_validations(api_client, data, error_field, error_message, user_to_authenticate=None, deposit=None):

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

    response = api_client.post(api_url('treasury_bond_transactions/'), data=data)

    assert response.status_code == 400
    assert str(response.data[error_field][0]) == error_message