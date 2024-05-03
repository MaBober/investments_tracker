import pytest

from django.utils import timezone

from wallets.models import MarketAssetTransaction, Deposit

from wallets.tests.test_fixture import test_user, test_currencies, test_countries
from wallets.tests.wallet.test_fixture import test_wallets
from wallets.tests.account.test_fixture import test_accounts, test_account_types, test_account_institution_types, test_institution
from wallets.tests.asset.test_fixture import test_asset_types, test_exchange_marketes, test_market_shares


@pytest.fixture
def test_market_asset_transactions(test_accounts, test_currencies, test_wallets, test_user, test_market_shares):
    market_asset_transactions = []
    market_asset_transactions_data = [
        {'asset':test_market_shares[0], 'wallet': test_wallets[0], 'account': test_accounts[0], 'user': test_user[0], 'amount': 100.00, 'currency': test_currencies[0],  'transaction_type': 'B', 'price': 100.00, 'commission': 1.00, 'commission_currency': test_currencies[0], 'commission_currency_price': 2.00, 'transaction_date': timezone.now()},
        {'asset':test_market_shares[0], 'wallet': test_wallets[0], 'account': test_accounts[0], 'user': test_user[0], 'amount': 200.00, 'currency': test_currencies[0],  'transaction_type': 'B', 'price': 200.00, 'commission': 1.00, 'commission_currency': test_currencies[0], 'commission_currency_price': 2.00, 'transaction_date': timezone.now()},
        {'asset':test_market_shares[0], 'wallet': test_wallets[0], 'account': test_accounts[0], 'user': test_user[0], 'amount': 300.00, 'currency': test_currencies[0],  'transaction_type': 'B', 'price': 300.00, 'commission': 1.00, 'commission_currency': test_currencies[0], 'commission_currency_price': 2.00, 'transaction_date': timezone.now()},
        {'asset':test_market_shares[0], 'wallet': test_wallets[0], 'account': test_accounts[0], 'user': test_user[0], 'amount': 400.00, 'currency': test_currencies[0],  'transaction_type': 'B', 'price': 400.00, 'commission': 1.00, 'commission_currency': test_currencies[0], 'commission_currency_price': 2.00, 'transaction_date': timezone.now()},
        {'asset':test_market_shares[0], 'wallet': test_wallets[0], 'account': test_accounts[0], 'user': test_user[0], 'amount': 500.00, 'currency': test_currencies[0],  'transaction_type': 'B', 'price': 500.00, 'commission': 1.00, 'commission_currency': test_currencies[0], 'commission_currency_price': 2.00, 'transaction_date': timezone.now()}
    ]

    for market_asset_transaction in market_asset_transactions_data:

        Deposit.objects.create(wallet=market_asset_transaction['wallet'],
                               account=market_asset_transaction['account'],
                                user=market_asset_transaction['user'],
                                amount=market_asset_transaction['amount'] * 5500,
                                currency=market_asset_transaction['currency'],
                                deposited_at=market_asset_transaction['transaction_date'])
        
        market_asset_transactions.append(MarketAssetTransaction.objects.create(
            asset=market_asset_transaction['asset'],
            wallet=market_asset_transaction['wallet'],
            account=market_asset_transaction['account'],
            user=market_asset_transaction['user'],
            amount=market_asset_transaction['amount'],
            currency=market_asset_transaction['currency'],
            transaction_type=market_asset_transaction['transaction_type'],
            price=market_asset_transaction['price'],
            commission=market_asset_transaction['commission'],
            commission_currency=market_asset_transaction['commission_currency'],
            commission_currency_price=market_asset_transaction['commission_currency_price'],
            transaction_date=market_asset_transaction['transaction_date']))
        
    return market_asset_transactions