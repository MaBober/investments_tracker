import pytest

from wallets.models import AssetType, ExchangeMarket
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