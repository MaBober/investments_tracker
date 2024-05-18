import pytest

from wallets.models import AssetType, ExchangeMarket, MarketShare, TreasuryBonds
from wallets.tests.test_fixture import test_countries, test_currencies


@pytest.fixture
def test_asset_types():

    asset_types = []
    asset_types_data = [
        {'name': 'Share', 'description': 'Share asset type'},
        {'name': 'ETF', 'description': 'ETF asset type'},
        {'name': 'Mutual Fund', 'description': 'Mutual Fund asset type'},
        {'name': 'Cryptocurrency', 'description': 'Cryptocurrency asset type'},
        {'name': 'Other', 'description': 'Other asset type'},
        {'name': 'Treasury Bonds', 'description': 'Treasury Bonds asset type'}
    ]

    for asset_type in asset_types_data:
        asset_types.append(AssetType.objects.create(name=asset_type['name'], description=asset_type['description']))

    return asset_types

@pytest.fixture
def test_exchange_marketes(test_countries, test_currencies):

    exchange_markets = []
    exchange_markets_data = [
        {'name': 'NYSE', 'country': test_countries[0], 'description': 'NYSE description', 'code': 'NYSE', 'prices_currency': test_currencies[0]},
        {'name': 'NASDAQ', 'country': test_countries[0], 'description': 'NASDAQ description', 'code': 'NASDAQ', 'prices_currency': test_currencies[0]},
        {'name': 'LSE', 'country': test_countries[1], 'description': 'LSE description', 'code': 'LSE', 'prices_currency': test_currencies[1]},
        {'name': 'JPX', 'country': test_countries[2], 'description': 'JPX description', 'code': 'JPX', 'prices_currency': test_currencies[2]},
        {'name': 'SSE', 'country': test_countries[3], 'description': 'SSE description', 'code': 'SSE', 'prices_currency': test_currencies[3]},
    ]

    for exchange_market in exchange_markets_data:
        exchange_markets.append(ExchangeMarket.objects.create(name=exchange_market['name'], country=exchange_market['country'], description=exchange_market['description'], code=exchange_market['code'], prices_currency=exchange_market['prices_currency']))

    return exchange_markets

@pytest.fixture
def test_market_shares(test_exchange_marketes, test_currencies, test_asset_types, test_countries):

    market_shares = []
    market_shares_data = [
        {'name': 'AAPL', 'code': 'AAPL', 'is_share': True, 'is_etf': False, 'description': 'AAPL description', 'exchange_market': test_exchange_marketes[0], 'price_currency': test_currencies[0], 'company_country': test_countries[0]},
        {'name': 'MSFT', 'code': 'MSFT', 'is_share': True, 'is_etf': False, 'description': 'MSFT description', 'exchange_market': test_exchange_marketes[0], 'price_currency': test_currencies[0], 'company_country': test_countries[0]},
        {'name': 'GOOGL', 'code': 'GOOGL', 'is_share': True, 'is_etf': False, 'description': 'GOOGL description', 'exchange_market': test_exchange_marketes[0], 'price_currency': test_currencies[0], 'company_country': test_countries[0]},
        {'name': 'AMZN', 'code': 'AMZN', 'is_share': True, 'is_etf': False, 'description': 'AMZN description', 'exchange_market': test_exchange_marketes[0], 'price_currency': test_currencies[0], 'company_country': test_countries[0]},
        {'name': 'TSLA', 'code': 'TSLA', 'is_share': True, 'is_etf': False, 'description': 'TSLA description', 'exchange_market': test_exchange_marketes[0], 'price_currency': test_currencies[0], 'company_country': test_countries[0]},
    ]

    for market_share in market_shares_data:
        market_shares.append(MarketShare.objects.create(name=market_share['name'], code=market_share['code'], is_share=market_share['is_share'], is_etf=market_share['is_etf'], description=market_share['description'], exchange_market=market_share['exchange_market'], price_currency=market_share['price_currency'], company_country=market_share['company_country']))

    return market_shares



@pytest.fixture
def test_treasury_bonds(test_currencies,  test_countries, test_asset_types):

    treasury_bonds = []
    treasury_bonds_data = [
        {'name': 'US Treasury Bonds', 'code': 'US-TB', 'description': 'US Treasury Bonds description', 'price_currency': test_currencies[0], 'issuer_country': test_countries[0], 'duration': 10, 'duration_unit': 'Y', 'initial_interest_rate': 0.5, 'premature_withdrawal_fee': 1, 'nominal_value': 100},
        {'name': 'UK Treasury Bonds', 'code': 'UK-TB', 'description': 'UK Treasury Bonds description', 'price_currency': test_currencies[1], 'issuer_country': test_countries[1], 'duration': 10, 'duration_unit': 'Y', 'initial_interest_rate': 0.5, 'premature_withdrawal_fee': 1, 'nominal_value': 120},
        {'name': 'JP Treasury Bonds', 'code': 'JP-TB', 'description': 'JP Treasury Bonds description', 'price_currency': test_currencies[2], 'issuer_country': test_countries[2], 'duration': 10, 'duration_unit': 'Y', 'initial_interest_rate': 0.5, 'premature_withdrawal_fee': 1, 'nominal_value': 120},
        {'name': 'CN Treasury Bonds', 'code': 'CN-TB', 'description': 'CN Treasury Bonds description', 'price_currency': test_currencies[3], 'issuer_country': test_countries[3], 'duration': 10, 'duration_unit': 'Y', 'initial_interest_rate': 0.5, 'premature_withdrawal_fee': 1, 'nominal_value': 130},
        {'name': 'DE Treasury Bonds', 'code': 'DE-TB', 'description': 'DE Treasury Bonds description', 'price_currency': test_currencies[4], 'issuer_country': test_countries[4], 'duration': 10, 'duration_unit': 'Y', 'initial_interest_rate': 0.5, 'premature_withdrawal_fee': 1, 'nominal_value': 140},
    ]

    for treasury_bond in treasury_bonds_data:
        treasury_bonds.append(TreasuryBonds.objects.create(
            name=treasury_bond['name'],
            code=treasury_bond['code'],
            description=treasury_bond['description'],
            price_currency=treasury_bond['price_currency'],
            issuer_country=treasury_bond['issuer_country'],
            duration=treasury_bond['duration'],
            duration_unit=treasury_bond['duration_unit'],
            initial_interest_rate=treasury_bond['initial_interest_rate'],
            premature_withdrawal_fee=treasury_bond['premature_withdrawal_fee'],
            nominal_value=treasury_bond['nominal_value']))

    return treasury_bonds