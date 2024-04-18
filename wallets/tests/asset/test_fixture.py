import pytest

from wallets.models import AssetType, ExchangeMarket, MarketShare
from wallets.tests.test_fixture import test_countries, test_currencies


@pytest.fixture
def test_asset_types():

    asset_types = []
    asset_types_data = [
        {'name': 'Share', 'description': 'Share asset type'},
        {'name': 'ETF', 'description': 'ETF asset type'},
        {'name': 'Mutual Fund', 'description': 'Mutual Fund asset type'},
        {'name': 'Cryptocurrency', 'description': 'Cryptocurrency asset type'},
        {'name': 'Other', 'description': 'Other asset type'}
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

