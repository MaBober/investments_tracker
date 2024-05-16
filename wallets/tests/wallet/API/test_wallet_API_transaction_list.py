import pytest

from django.utils import timezone

from wallets.tests.test_fixture import test_user, authenticated_client, api_client, admin_logged_client, api_url, test_currencies, test_countries
from wallets.tests.account.test_fixture import test_accounts, test_account_types, test_account_institution_types, test_institution
from wallets.tests.asset.test_fixture import test_asset_types, test_exchange_marketes, test_market_shares, test_treasury_bonds
from wallets.tests.wallet.test_fixture import test_wallets
from wallets.tests.deposit.test_fixture import test_deposits
from wallets.tests.transaction.test_fixture import test_market_asset_transactions

from wallets.models import Deposit, MarketAssetTransaction, TreasuryBondsTransaction

@pytest.mark.django_db
def test_wallet_transaction_list_owner_empty_list(api_client, test_wallets, test_user):

    user = test_user[0]
    wallet = test_wallets[0]
    wallet.owner = user
    wallet.save()

    api_client.force_authenticate(user=user)

    response = api_client.get(api_url(f'wallets/{wallet.id}/transactions/'))

    assert response.status_code == 200
    assert response.data['count'] == 0
    assert response.data['results'] == []



@pytest.mark.django_db
def test_wallet_transaction_list_co_owner_empty_list(api_client, test_wallets, test_user):

    user = test_user[0]
    wallet = test_wallets[0]

    wallet.owner = test_user[1]
    wallet.co_owners.clear()
    wallet.co_owners.add(user)
    wallet.save()

    api_client.force_authenticate(user=user)

    response = api_client.get(api_url(f'wallets/{wallet.id}/transactions/'))

    assert response.status_code == 200
    assert response.data['count'] == 0
    assert response.data['results'] == []


@pytest.mark.django_db
def test_wallet_transaction_list_not_owner_nor_co_owner_empty_list(api_client, test_wallets, test_user):

    user = test_user[0]
    wallet = test_wallets[0]

    wallet.owner = test_user[1]
    wallet.co_owners.clear()
    wallet.save()

    api_client.force_authenticate(user=user)

    response = api_client.get(api_url(f'wallets/{wallet.id}/transactions/'))

    assert response.status_code == 403


@pytest.mark.django_db
def test_wallet_transaction_list_owner_list(api_client, test_market_shares, test_wallets, test_accounts, test_currencies, test_user):

    user = test_user[0]
    wallet = test_wallets[0]
    test_wallets[0].owner = user
    test_wallets[0].save()

    api_client.force_authenticate(user=user)

    #make deposit to wallet

    deposit = Deposit.objects.create(
        user=user,
        wallet=wallet,
        account=wallet.accounts.first(),
        amount=1000000,
        currency=wallet.accounts.first().currencies.first(),
        deposited_at=timezone.now()
    )

    #make transaction

    transaction_data = {
        'user': test_user[0],
        'transaction_type': 'B',
        'account': test_accounts[0],
        'wallet': test_wallets[0],
        'asset': test_market_shares[0],
        'amount': 100.00,
        'price': 1.00,
        'currency': test_currencies[0],
        'currency_price': 1.00,
        'commission': 0.00,
        'commission_currency': test_currencies[0],
        'commission_currency_price': 1.00,
        'transaction_date': timezone.now()
    }

    transaction = MarketAssetTransaction.objects.create(**transaction_data)

    transaction_data['asset'] = test_market_shares[1]
    transaction_data['amount'] = 50.00
    transaction_data['price'] = 2.00

    transaction = MarketAssetTransaction.objects.create(**transaction_data)

    response = api_client.get(api_url(f'wallets/{wallet.id}/transactions/'))

    assert response.status_code == 200
    assert response.data['count'] == 2
    assert response.data['results'][0]['amount'] ==  "{:.2f}".format(100)
    assert response.data['results'][1]['amount'] == "{:.2f}".format(50)
    assert response.data['results'][0]['price'] == "{:.2f}".format(1.00)
    assert response.data['results'][1]['price'] == '{:.2f}'.format(2.00)
    assert response.data['results'][0]['transaction_type'] == 'B'
    assert response.data['results'][1]['transaction_type'] == 'B'
    assert response.data['results'][0]['currency'] == test_currencies[0].code
    assert response.data['results'][1]['currency'] == test_currencies[0].code
    assert response.data['results'][0]['commission'] == "{:.2f}".format(0.00)
    assert response.data['results'][1]['commission'] == "{:.2f}".format(0.00)
    assert response.data['results'][0]['commission_currency'] == test_currencies[0].code
    assert response.data['results'][1]['commission_currency'] == test_currencies[0].code
    assert response.data['results'][0]['total_price'] != 0
    assert response.data['results'][1]['total_price'] != 0
    

##TODO: Make test for GET with parameters

@pytest.mark.django_db
def test_wallet_transaction_list_owner_list_with_parameters(api_client, test_market_shares, test_wallets, test_accounts, test_currencies, test_user):

    user = test_user[0]
    wallet = test_wallets[0]
    test_wallets[0].owner = user
    test_wallets[0].save()

    api_client.force_authenticate(user=user)

    #make deposit to account

    deposit = Deposit.objects.create(
        user=user,
        wallet=wallet,
        account=wallet.accounts.first(),
        amount=1000000,
        currency=wallet.accounts.first().currencies.first(),
        deposited_at=timezone.now()
    )

    #make transaction

    transaction_data = {
        'user': test_user[0],
        'transaction_type': 'B',
        'account': test_accounts[0],
        'wallet': test_wallets[0],
        'asset': test_market_shares[0],
        'amount': 100.00,
        'price': 1.00,
        'currency': test_currencies[0],
        'currency_price': 1.00,
        'commission': 0.00,
        'commission_currency': test_currencies[0],
        'commission_currency_price': 1.00,
        'transaction_date': timezone.now()
    }

    transaction = MarketAssetTransaction.objects.create(**transaction_data)

    transaction_data['asset'] = test_market_shares[1]
    transaction_data['amount'] = 50.00
    transaction_data['price'] = 2.00

    transaction = MarketAssetTransaction.objects.create(**transaction_data)

    response = api_client.get(api_url(f'wallets/{wallet.id}/transactions/?transaction_type=B'))

    assert response.status_code == 200
    assert response.data['count'] == 2
    assert response.data['results'][0]['amount'] ==  "{:.2f}".format(100)
    assert response.data['results'][1]['amount'] == "{:.2f}".format(50)
    assert response.data['results'][0]['price'] == "{:.2f}".format(1.00)
    assert response.data['results'][1]['price'] == '{:.2f}'.format(2.00)
    assert response.data['results'][0]['transaction_type'] == 'B'
    assert response.data['results'][1]['transaction_type'] == 'B'
    assert response.data['results'][0]['currency'] == test_currencies[0].code

    response = api_client.get(api_url(f'wallets/{wallet.id}/transactions/?transaction_type=S'))

    assert response.status_code == 200
    assert response.data['count'] == 0
    assert response.data['results'] == []




@pytest.mark.django_db
def test_wallet_treasury_bond_transaction_list_owner_empty_list(api_client, test_wallets, test_user):

    user = test_user[0]
    wallet = test_wallets[0]
    wallet.owner = user
    wallet.save()

    api_client.force_authenticate(user=user)

    response = api_client.get(api_url(f'wallets/{wallet.id}/treasury_bond_transactions/'))

    assert response.status_code == 200
    assert response.data['count'] == 0
    assert response.data['results'] == []


@pytest.mark.django_db
def test_wallet_treasury_bond_transaction_list_co_owner_empty_list(api_client, test_wallets, test_user):

    user = test_user[0]
    wallet = test_wallets[0]

    wallet.owner = test_user[1]
    wallet.co_owners.clear()
    wallet.co_owners.add(user)
    wallet.save()

    api_client.force_authenticate(user=user)

    response = api_client.get(api_url(f'wallets/{wallet.id}/treasury_bond_transactions/'))

    assert response.status_code == 200
    assert response.data['count'] == 0
    assert response.data['results'] == []


@pytest.mark.django_db
def test_wallet_treasury_bond_transaction_list_not_owner_nor_co_owner_empty_list(api_client, test_wallets, test_user):

    user = test_user[0]
    wallet = test_wallets[0]

    wallet.owner = test_user[1]
    wallet.co_owners.clear()
    wallet.save()

    api_client.force_authenticate(user=user)

    response = api_client.get(api_url(f'wallets/{wallet.id}/treasury_bond_transactions/'))

    assert response.status_code == 403


@pytest.mark.django_db
def test_wallet_treasury_bond_transaction_list_owner_list(api_client, test_treasury_bonds, test_wallets, test_accounts, test_currencies, test_user):

    user = test_user[0]
    wallet = test_wallets[0]
    test_wallets[0].owner = user
    test_wallets[0].save()

    api_client.force_authenticate(user=user)

    #make deposit to wallet

    deposit = Deposit.objects.create(
        user=user,
        account=wallet.accounts.first(),
        wallet=wallet,
        amount=1000000,
        currency=wallet.accounts.first().currencies.first(),
        deposited_at=timezone.now()
    )

    #make transaction

    transaction_data = {
        'user': test_user[0],
        'transaction_type': 'B',
        'account': test_accounts[0],
        'wallet': test_wallets[0],
        'bond': test_treasury_bonds[0],
        'amount': 100.00,
        'price': 1.00,
        'currency': test_currencies[0],
        'commission': 0.00,
        'commission_currency': test_currencies[0],
        'commission_currency_price': 1.00,
        'transaction_date': timezone.now()
    }

    transaction = TreasuryBondsTransaction.objects.create(**transaction_data)

    transaction_data['bond'] = test_treasury_bonds[1]
    transaction_data['amount'] = 50.00
    transaction_data['price'] = 2.00

    transaction = TreasuryBondsTransaction.objects.create(**transaction_data)

    response = api_client.get(api_url(f'wallets/{wallet.id}/treasury_bond_transactions/'))

    assert response.status_code == 200
    assert response.data['count'] == 2
    assert response.data['results'][0]['amount'] ==  "{:.2f}".format(100)
    assert response.data['results'][1]['amount'] == "{:.2f}".format(50)
    assert response.data['results'][0]['price'] == "{:.2f}".format(1.00)
    assert response.data['results'][1]['price'] == '{:.2f}'.format(2.00)
    assert response.data['results'][0]['transaction_type'] == 'B'
    assert response.data['results'][1]['transaction_type'] == 'B'
    assert response.data['results'][0]['currency'] == test_currencies[0].code
    assert response.data['results'][1]['currency'] == test_currencies[0].code
    assert response.data['results'][0]['commission'] == "{:.2f}".format(0.00)
    assert response.data['results'][1]['commission'] == "{:.2f}".format(0.00)
    assert response.data['results'][0]['commission_currency'] == test_currencies[0].code
    assert response.data['results'][1]['commission_currency'] == test_currencies[0].code
    assert response.data['results'][0]['total_price'] != 0  
    assert response.data['results'][1]['total_price'] != 0 


@pytest.mark.django_db
def test_wallet_treasury_bond_transaction_lis_with_parameters(api_client, test_treasury_bonds, test_wallets, test_accounts, test_currencies, test_user):

    user = test_user[0]
    wallet = test_wallets[0]
    test_wallets[0].owner = user
    test_wallets[0].save()

    api_client.force_authenticate(user=user)

    #make deposit to wallet

    deposit = Deposit.objects.create(
        user=user,
        account=wallet.accounts.first(),
        wallet=wallet,
        amount=1000000,
        currency=wallet.accounts.first().currencies.first(),
        deposited_at=timezone.now()
    )

    #make transaction

    transaction_data = {
        'user': test_user[0],
        'transaction_type': 'B',
        'account': test_accounts[0],
        'wallet': test_wallets[0],
        'bond': test_treasury_bonds[0],
        'amount': 100.00,
        'price': 1.00,
        'currency': test_currencies[0],
        'commission': 0.00,
        'commission_currency': test_currencies[0],
        'commission_currency_price': 1.00,
        'transaction_date': timezone.now()
    }

    transaction = TreasuryBondsTransaction.objects.create(**transaction_data)

    transaction_data['bond'] = test_treasury_bonds[1]
    transaction_data['amount'] = 50.00
    transaction_data['price'] = 2.00

    transaction = TreasuryBondsTransaction.objects.create(**transaction_data)

    response = api_client.get(api_url(f'wallets/{wallet.id}/treasury_bond_transactions/?transaction_type=B?currency={test_currencies[0].code}'))

    assert response.status_code == 200
    assert response.data['count'] == 2
    assert response.data['results'][0]['amount'] ==  "{:.2f}".format(100)
    assert response.data['results'][1]['amount'] == "{:.2f}".format(50)
    assert response.data['results'][0]['price'] == "{:.2f}".format(1.00)
    assert response.data['results'][1]['price'] == '{:.2f}'.format(2.00)
    assert response.data['results'][0]['transaction_type'] == 'B'
    assert response.data['results'][1]['transaction_type'] == 'B'
    assert response.data['results'][0]['currency'] == test_currencies[0].code