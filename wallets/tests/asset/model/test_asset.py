import pytest

from django.utils import timezone
from django.core.exceptions import ValidationError

from wallets.tests.test_fixture import test_countries, test_currencies
from wallets.tests.asset.test_fixture import test_asset_types, test_exchange_marketes

from wallets.models import AssetType, ExchangeMarket, MarketShare, AssetTypeAssociation, MarketETF


@pytest.mark.django_db
def test_asset_type_create():

    AssetType.objects.create(name='Shares', description='Shares description')

    assert AssetType.objects.count() == 1

    asset_type = AssetType.objects.first()

    assert asset_type.name == 'Shares'
    assert asset_type.description == 'Shares description'
    assert asset_type.created_at is not None
    assert asset_type.updated_at is not None
    assert str(asset_type) == 'Shares'
    assert timezone.now() - asset_type.created_at < timezone.timedelta(seconds=1.5)


@pytest.mark.django_db
def test_asset_type_create_duplicate():

    AssetType.objects.create(name='Shares', description='Shares description')

    with pytest.raises(ValidationError) as exception_info:
        AssetType.objects.create(name='Shares', description='Shares description')

    assert str(exception_info.value.error_dict.get('name')[0]) == "['Asset type with this Name already exists.']"
    assert AssetType.objects.count() == 1

@pytest.mark.django_db
def test_asset_type_create_blank_name():

    with pytest.raises(ValidationError) as exception_info:
        AssetType.objects.create(name='', description='Shares description')

    assert str(exception_info.value.error_dict.get('name')[0]) == "['This field cannot be blank.']"
    assert AssetType.objects.count() == 0

@pytest.mark.django_db
def test_asset_type_create_name_too_long():

    with pytest.raises(ValidationError) as exception_info:
        AssetType.objects.create(name='a' * 101, description='Shares description')

    assert str(exception_info.value.error_dict.get('name')[0]) == "['Ensure this value has at most 100 characters (it has 101).']"
    assert AssetType.objects.count() == 0

@pytest.mark.django_db
def test_asset_type_create_too_long_description():

    with pytest.raises(ValidationError) as exception_info:
        AssetType.objects.create(name='Shares', description='a' * 1001)

    assert str(exception_info.value.error_dict.get('description')[0]) == "['Ensure this value has at most 1000 characters (it has 1001).']"
    assert AssetType.objects.count() == 0

@pytest.mark.django_db
def test_asset_type_update():

    asset_type = AssetType.objects.create(name='Shares', description='Shares description')

    asset_type.name = 'ETFs'
    asset_type.description = 'ETFs description'
    asset_type.save()

    assert AssetType.objects.count() == 1

    asset_type = AssetType.objects.first()

    assert asset_type.name == 'ETFs'
    assert asset_type.description == 'ETFs description'
    assert asset_type.created_at is not None
    assert asset_type.updated_at is not None
    assert str(asset_type) == 'ETFs'
    assert timezone.now() - asset_type.updated_at < timezone.timedelta(seconds=1.5)

@pytest.mark.django_db
def test_asset_type_update_duplicate():

    AssetType.objects.create(name='Shares', description='Shares description')
    AssetType.objects.create(name='ETFs', description='ETFs description')

    asset_type = AssetType.objects.get(name='Shares')

    with pytest.raises(ValidationError) as exception_info:
        asset_type.name = 'ETFs'
        asset_type.save()

    assert str(exception_info.value.error_dict.get('name')[0]) == "['Asset type with this Name already exists.']"
    assert AssetType.objects.count() == 2

@pytest.mark.django_db
def test_asset_type_update_blank_name():

    asset_type = AssetType.objects.create(name='Shares', description='Shares description')

    with pytest.raises(ValidationError) as exception_info:
        asset_type.name = ''
        asset_type.save()

    assert str(exception_info.value.error_dict.get('name')[0]) == "['This field cannot be blank.']"
    assert AssetType.objects.count() == 1

@pytest.mark.django_db
def test_asset_type_update_name_too_long():

    asset_type = AssetType.objects.create(name='Shares', description='Shares description')

    with pytest.raises(ValidationError) as exception_info:
        asset_type.name = 'a' * 101
        asset_type.save()

    assert str(exception_info.value.error_dict.get('name')[0]) == "['Ensure this value has at most 100 characters (it has 101).']"
    assert AssetType.objects.count() == 1

@pytest.mark.django_db
def test_asset_type_update_too_long_description():
    
    asset_type = AssetType.objects.create(name='Shares', description='Shares description')

    with pytest.raises(ValidationError) as exception_info:
        asset_type.description = 'a' * 1001
        asset_type.save()

    assert str(exception_info.value.error_dict.get('description')[0]) == "['Ensure this value has at most 1000 characters (it has 1001).']"
    assert AssetType.objects.count() == 1

@pytest.mark.django_db
def test_asset_type_delete():

    asset_type = AssetType.objects.create(name='Shares', description='Shares description')

    asset_type.delete()

    assert AssetType.objects.count() == 0

@pytest.mark.django_db
def test_exchange_market_create(test_countries, test_currencies):

    ExchangeMarket.objects.create(name='NYSE', code='NYSE', description='NYSE description', prices_currency=test_currencies[0], country=test_countries[0])

    assert ExchangeMarket.objects.count() == 1

    exchange_market = ExchangeMarket.objects.first()

    assert exchange_market.name == 'NYSE'
    assert exchange_market.code == 'NYSE'
    assert exchange_market.description == 'NYSE description'
    assert exchange_market.prices_currency == test_currencies[0]
    assert exchange_market.country == test_countries[0]
    assert exchange_market.created_at is not None
    assert exchange_market.updated_at is not None
    assert str(exchange_market) == 'NYSE'
    assert timezone.now() - exchange_market.created_at < timezone.timedelta(seconds=1.5)

@pytest.mark.django_db
def test_exchange_market_create_duplicate(test_countries, test_currencies):

    ExchangeMarket.objects.create(name='NYSE', code='NYSE', description='NYSE description', prices_currency=test_currencies[0], country=test_countries[0])

    with pytest.raises(ValidationError) as exception_info:
        ExchangeMarket.objects.create(name='NYSE', code='NYSE', description='NYSE description', prices_currency=test_currencies[0], country=test_countries[0])

    assert str(exception_info.value.error_dict.get('name')[0]) == "['Exchange market with this Name already exists.']"
    assert ExchangeMarket.objects.count() == 1

@pytest.mark.django_db
def test_exchange_market_create_blank_name(test_countries, test_currencies):

    with pytest.raises(ValidationError) as exception_info:
        ExchangeMarket.objects.create(name='', code='NYSE', description='NYSE description', prices_currency=test_currencies[0], country=test_countries[0])

    assert str(exception_info.value.error_dict.get('name')[0]) == "['This field cannot be blank.']"
    assert ExchangeMarket.objects.count() == 0

@pytest.mark.django_db
def test_exchange_market_create_name_too_long(test_countries, test_currencies):

    with pytest.raises(ValidationError) as exception_info:
        ExchangeMarket.objects.create(name='a' * 101, code='NYSE', description='NYSE description', prices_currency=test_currencies[0], country=test_countries[0])

    assert str(exception_info.value.error_dict.get('name')[0]) == "['Ensure this value has at most 100 characters (it has 101).']"
    assert ExchangeMarket.objects.count() == 0

@pytest.mark.django_db
def test_exchange_market_create_blank_code(test_countries, test_currencies):

    with pytest.raises(ValidationError) as exception_info:
        ExchangeMarket.objects.create(name='NYSE', code='', description='NYSE description', prices_currency=test_currencies[0], country=test_countries[0])

    assert str(exception_info.value.error_dict.get('code')[0]) == "['This field cannot be blank.']"
    assert ExchangeMarket.objects.count() == 0

@pytest.mark.django_db
def test_exchange_market_create_code_too_long(test_countries, test_currencies):

    with pytest.raises(ValidationError) as exception_info:
        ExchangeMarket.objects.create(name='NYSE', code='a' * 101, description='NYSE description', prices_currency=test_currencies[0], country=test_countries[0])

    assert str(exception_info.value.error_dict.get('code')[0]) == "['Ensure this value has at most 100 characters (it has 101).']"
    assert ExchangeMarket.objects.count() == 0

@pytest.mark.django_db
def test_exchange_market_create_too_long_description(test_countries, test_currencies):

    with pytest.raises(ValidationError) as exception_info:
        ExchangeMarket.objects.create(name='NYSE', code='NYSE', description='a' * 1001, prices_currency=test_currencies[0], country=test_countries[0])

    assert str(exception_info.value.error_dict.get('description')[0]) == "['Ensure this value has at most 1000 characters (it has 1001).']"
    assert ExchangeMarket.objects.count() == 0

@pytest.mark.django_db
def test_exchange_market_create_no_prices_currency(test_countries):

    with pytest.raises(ValidationError) as exception_info:
        ExchangeMarket.objects.create(name='NYSE', code='NYSE', description='NYSE description', country=test_countries[0])

    assert str(exception_info.value.error_dict.get('prices_currency')[0]) == "['This field cannot be null.']"
    assert ExchangeMarket.objects.count() == 0

@pytest.mark.django_db
def test_exchange_market_create_no_country(test_currencies):

    with pytest.raises(ValidationError) as exception_info:
        ExchangeMarket.objects.create(name='NYSE', code='NYSE', description='NYSE description', prices_currency=test_currencies[0])

    assert str(exception_info.value.error_dict.get('country')[0]) == "['This field cannot be null.']"
    assert ExchangeMarket.objects.count() == 0

@pytest.mark.django_db
def test_exchange_market_update(test_countries, test_currencies):

    exchange_market = ExchangeMarket.objects.create(name='NYSE', code='NYSE', description='NYSE description', prices_currency=test_currencies[0], country=test_countries[0])

    exchange_market.name = 'NASDAQ'
    exchange_market.code = 'NASDAQ'
    exchange_market.description = 'NASDAQ description'
    exchange_market.prices_currency = test_currencies[1]
    exchange_market.country = test_countries[1]
    exchange_market.save()

    assert ExchangeMarket.objects.count() == 1

    exchange_market = ExchangeMarket.objects.first()

    assert exchange_market.name == 'NASDAQ'
    assert exchange_market.code == 'NASDAQ'
    assert exchange_market.description == 'NASDAQ description'
    assert exchange_market.prices_currency == test_currencies[1]
    assert exchange_market.country == test_countries[1]
    assert exchange_market.created_at is not None
    assert exchange_market.updated_at is not None
    assert str(exchange_market) == 'NASDAQ'
    assert timezone.now() - exchange_market.updated_at < timezone.timedelta(seconds=1.5)

@pytest.mark.django_db
def test_exchange_market_update_duplicate(test_countries, test_currencies):

    ExchangeMarket.objects.create(name='NYSE', code='NYSE', description='NYSE description', prices_currency=test_currencies[0], country=test_countries[0])
    ExchangeMarket.objects.create(name='NASDAQ', code='NASDAQ', description='NASDAQ description', prices_currency=test_currencies[1], country=test_countries[1])

    exchange_market = ExchangeMarket.objects.get(name='NYSE')

    with pytest.raises(ValidationError) as exception_info:
        exchange_market.name = 'NASDAQ'
        exchange_market.save()

    assert str(exception_info.value.error_dict.get('name')[0]) == "['Exchange market with this Name already exists.']"
    assert ExchangeMarket.objects.count() == 2

@pytest.mark.django_db
def test_exchange_market_update_blank_name(test_countries, test_currencies):

    exchange_market = ExchangeMarket.objects.create(name='NYSE', code='NYSE', description='NYSE description', prices_currency=test_currencies[0], country=test_countries[0])

    with pytest.raises(ValidationError) as exception_info:
        exchange_market.name = ''
        exchange_market.save()

    assert str(exception_info.value.error_dict.get('name')[0]) == "['This field cannot be blank.']"
    assert ExchangeMarket.objects.count() == 1

@pytest.mark.django_db
def test_exchange_market_update_name_too_long(test_countries, test_currencies):

    exchange_market = ExchangeMarket.objects.create(name='NYSE', code='NYSE', description='NYSE description', prices_currency=test_currencies[0], country=test_countries[0])

    with pytest.raises(ValidationError) as exception_info:
        exchange_market.name = 'a' * 101
        exchange_market.save()

    assert str(exception_info.value.error_dict.get('name')[0]) == "['Ensure this value has at most 100 characters (it has 101).']"
    assert ExchangeMarket.objects.count() == 1

@pytest.mark.django_db
def test_exchange_market_update_blank_code(test_countries, test_currencies):

    exchange_market = ExchangeMarket.objects.create(name='NYSE', code='NYSE', description='NYSE description', prices_currency=test_currencies[0], country=test_countries[0])

    with pytest.raises(ValidationError) as exception_info:
        exchange_market.code = ''
        exchange_market.save()

    assert str(exception_info.value.error_dict.get('code')[0]) == "['This field cannot be blank.']"
    assert ExchangeMarket.objects.count() == 1

@pytest.mark.django_db
def test_exchange_market_update_code_too_long(test_countries, test_currencies):

    exchange_market = ExchangeMarket.objects.create(name='NYSE', code='NYSE', description='NYSE description', prices_currency=test_currencies[0], country=test_countries[0])

    with pytest.raises(ValidationError) as exception_info:
        exchange_market.code = 'a' * 101
        exchange_market.save()

    assert str(exception_info.value.error_dict.get('code')[0]) == "['Ensure this value has at most 100 characters (it has 101).']"
    assert ExchangeMarket.objects.count() == 1

@pytest.mark.django_db
def test_exchange_market_update_too_long_description(test_countries, test_currencies):

    exchange_market = ExchangeMarket.objects.create(name='NYSE', code='NYSE', description='NYSE description', prices_currency=test_currencies[0], country=test_countries[0])

    with pytest.raises(ValidationError) as exception_info:
        exchange_market.description = 'a' * 1001
        exchange_market.save()

    assert str(exception_info.value.error_dict.get('description')[0]) == "['Ensure this value has at most 1000 characters (it has 1001).']"
    assert ExchangeMarket.objects.count() == 1

@pytest.mark.django_db
def test_exchange_market_update_no_prices_currency(test_countries, test_currencies):

    exchange_market = ExchangeMarket.objects.create(name='NYSE', code='NYSE', description='NYSE description', prices_currency=test_currencies[0], country=test_countries[0])

    with pytest.raises(ValidationError) as exception_info:
        exchange_market.prices_currency = None
        exchange_market.save()

    assert str(exception_info.value.error_dict.get('prices_currency')[0]) == "['This field cannot be null.']"
    assert ExchangeMarket.objects.count() == 1

@pytest.mark.django_db
def test_exchange_market_update_no_country(test_countries, test_currencies):

    exchange_market = ExchangeMarket.objects.create(name='NYSE', code='NYSE', description='NYSE description', prices_currency=test_currencies[0], country=test_countries[0])

    with pytest.raises(ValidationError) as exception_info:
        exchange_market.country = None
        exchange_market.save()

    assert str(exception_info.value.error_dict.get('country')[0]) == "['This field cannot be null.']"
    assert ExchangeMarket.objects.count() == 1

@pytest.mark.django_db
def test_exchange_market_delete(test_countries, test_currencies):

    exchange_market = ExchangeMarket.objects.create(name='NYSE', code='NYSE', description='NYSE description', prices_currency=test_currencies[0], country=test_countries[0])

    exchange_market.delete()

    assert ExchangeMarket.objects.count() == 0

@pytest.mark.django_db
def test_market_share_create(test_countries, test_currencies, test_asset_types, test_exchange_marketes):

    market_share = MarketShare.objects.create(
        name='AAPL',
        code='AAPL',
        description='AAPL description',
        exchange_market=test_exchange_marketes[0],
        price_currency=test_currencies[0],
        company_country=test_countries[0])

    assert MarketShare.objects.count() == 1

    market_share = MarketShare.objects.first()

    assert market_share.name == 'AAPL'
    assert market_share.code == 'AAPL'
    assert market_share.description == 'AAPL description'
    assert market_share.exchange_market == test_exchange_marketes[0]
    assert market_share.price_currency == test_currencies[0]
    assert market_share.company_country == test_countries[0]
    assert market_share.is_share == True
    assert market_share.created_at is not None
    assert market_share.updated_at is not None
    assert str(market_share) == 'AAPL'
    assert timezone.now() - market_share.created_at < timezone.timedelta(seconds=1.5)


    assert AssetTypeAssociation.objects.count() == 1
    for asset_type in market_share.assettypeassociation_set.all():

        assert asset_type.asset == market_share
        assert asset_type.asset_type == AssetType.objects.get(name='Share')
        assert asset_type.percentage == 1



@pytest.mark.django_db
def test_market_share_create_duplicated_exchange_and_code(test_countries, test_currencies, test_asset_types, test_exchange_marketes):

    MarketShare.objects.create(
        name='AAPL',
        code='AAPL',
        description='AAPL description',
        exchange_market=test_exchange_marketes[0],
        price_currency=test_currencies[0],
        company_country=test_countries[0])

    with pytest.raises(ValidationError) as exception_info:
        MarketShare.objects.create(
            name='AAPL',
            code='AAPL',
            description='AAPL description',
            exchange_market=test_exchange_marketes[0],
            price_currency=test_currencies[0],
            company_country=test_countries[0])


    assert str(exception_info.value.error_dict.get('__all__')[0]) == "['Market asset with this Exchange market and Code already exists.']"
    assert MarketShare.objects.count() == 1

@pytest.mark.django_db
def test_market_share_creat_duplicated_code_diffrent_exchange(test_countries, test_currencies, test_asset_types, test_exchange_marketes):

    MarketShare.objects.create(
        name='AAPL',
        code='AAPL',
        description='AAPL description',
        exchange_market=test_exchange_marketes[0],
        price_currency=test_currencies[0],
        company_country=test_countries[0])

    MarketShare.objects.create(
        name='AAPL',
        code='AAPL',
        description='AAPL description',
        exchange_market=test_exchange_marketes[1],
        price_currency=test_currencies[0],
        company_country=test_countries[0])

    assert MarketShare.objects.count() == 2

@pytest.mark.django_db
def test_market_share_create_blank_name(test_countries, test_currencies, test_asset_types, test_exchange_marketes):

    with pytest.raises(ValidationError) as exception_info:
        MarketShare.objects.create(
            name='',
            code='AAPL',
            description='AAPL description',
            exchange_market=test_exchange_marketes[0],
            price_currency=test_currencies[0],
            company_country=test_countries[0])

    assert str(exception_info.value.error_dict.get('name')[0]) == "['This field cannot be blank.']"
    assert MarketShare.objects.count() == 0

@pytest.mark.django_db
def test_market_share_create_name_too_long(test_countries, test_currencies, test_asset_types, test_exchange_marketes):

    with pytest.raises(ValidationError) as exception_info:
        MarketShare.objects.create(
            name='a' * 101,
            code='AAPL',
            description='AAPL description',
            exchange_market=test_exchange_marketes[0],
            price_currency=test_currencies[0],
            company_country=test_countries[0])

    assert str(exception_info.value.error_dict.get('name')[0]) == "['Ensure this value has at most 100 characters (it has 101).']"
    assert MarketShare.objects.count() == 0

@pytest.mark.django_db
def test_market_share_create_blank_code(test_countries, test_currencies, test_asset_types, test_exchange_marketes):

    with pytest.raises(ValidationError) as exception_info:
        MarketShare.objects.create(
            name='AAPL',
            code='',
            description='AAPL description',
            exchange_market=test_exchange_marketes[0],
            price_currency=test_currencies[0],
            company_country=test_countries[0])

    assert str(exception_info.value.error_dict.get('code')[0]) == "['This field cannot be blank.']"
    assert MarketShare.objects.count() == 0
    
@pytest.mark.django_db
def test_market_share_create_code_too_long(test_countries, test_currencies, test_asset_types, test_exchange_marketes):

    with pytest.raises(ValidationError) as exception_info:
        MarketShare.objects.create(
            name='AAPL',
            code='a' * 101,
            description='AAPL description',
            exchange_market=test_exchange_marketes[0],
            price_currency=test_currencies[0],
            company_country=test_countries[0])

    assert str(exception_info.value.error_dict.get('code')[0]) == "['Ensure this value has at most 100 characters (it has 101).']"
    assert MarketShare.objects.count() == 0

@pytest.mark.django_db
def test_market_share_create_too_long_description(test_countries, test_currencies, test_asset_types, test_exchange_marketes):

    with pytest.raises(ValidationError) as exception_info:
        MarketShare.objects.create(
            name='AAPL',
            code='AAPL',
            description='a' * 1001,
            exchange_market=test_exchange_marketes[0],
            price_currency=test_currencies[0],
            company_country=test_countries[0])

    assert str(exception_info.value.error_dict.get('description')[0]) == "['Ensure this value has at most 1000 characters (it has 1001).']"
    assert MarketShare.objects.count() == 0

@pytest.mark.django_db
def test_market_share_create_no_exchange_market(test_countries, test_currencies):

    with pytest.raises(ValidationError) as exception_info:
        MarketShare.objects.create(
            name='AAPL',
            code='AAPL',
            description='AAPL description',
            price_currency=test_currencies[0],
            company_country=test_countries[0])

    assert str(exception_info.value.error_dict.get('exchange_market')[0]) == "['This field cannot be null.']"
    assert MarketShare.objects.count() == 0

@pytest.mark.django_db
def test_market_share_create_no_price_currency(test_countries, test_exchange_marketes):

    with pytest.raises(ValidationError) as exception_info:
        MarketShare.objects.create(
            name='AAPL',
            code='AAPL',
            description='AAPL description',
            exchange_market=test_exchange_marketes[0],
            company_country=test_countries[0])

    assert str(exception_info.value.error_dict.get('price_currency')[0]) == "['This field cannot be null.']"
    assert MarketShare.objects.count() == 0

@pytest.mark.django_db
def test_market_share_create_no_company_country(test_currencies, test_exchange_marketes):

    with pytest.raises(ValidationError) as exception_info:
        MarketShare.objects.create(
            name='AAPL',
            code='AAPL',
            description='AAPL description',
            exchange_market=test_exchange_marketes[0],
            price_currency=test_currencies[0])

    assert str(exception_info.value.error_dict.get('company_country')[0]) == "['This field cannot be null.']"
    assert MarketShare.objects.count() == 0

@pytest.mark.django_db
def test_market_share_create_add_diffrent_asset_type(test_countries, test_currencies, test_asset_types, test_exchange_marketes):

    asset_type = AssetType.objects.create(name='ETFs', description='ETFs description')

    market_share = MarketShare.objects.create(
        name='AAPL',
        code='AAPL',
        description='AAPL description',
        exchange_market=test_exchange_marketes[0],
        price_currency=test_currencies[0],
        company_country=test_countries[0])

    with pytest.raises(ValidationError) as exception_info:
        AssetTypeAssociation.objects.create(asset=market_share, asset_type=asset_type, percentage=1)

    assert str(exception_info.value.error_dict.get('__all__')[0]) == "['MarketShare must have AssetType Share with percentage 1']"

    assert AssetTypeAssociation.objects.count() == 1
    for asset_type in market_share.assettypeassociation_set.all():

        assert asset_type.asset == market_share
        assert asset_type.asset_type == AssetType.objects.get(name='Share')
        assert asset_type.percentage == 1

@pytest.mark.django_db
def test_market_share_update(test_countries, test_currencies, test_asset_types, test_exchange_marketes):

    market_share = MarketShare.objects.create(
        name='AAPL',
        code='AAPL',
        description='AAPL description',
        exchange_market=test_exchange_marketes[0],
        price_currency=test_currencies[0],
        company_country=test_countries[0])

    market_share.name = 'GOOGL'
    market_share.code = 'GOOGL'
    market_share.description = 'GOOGL description'
    market_share.exchange_market = test_exchange_marketes[1]
    market_share.price_currency = test_currencies[1]
    market_share.company_country = test_countries[1]
    market_share.save()

    assert MarketShare.objects.count() == 1

    market_share = MarketShare.objects.first()

    assert market_share.name == 'GOOGL'
    assert market_share.code == 'GOOGL'
    assert market_share.description == 'GOOGL description'
    assert market_share.exchange_market == test_exchange_marketes[1]
    assert market_share.price_currency == test_currencies[1]
    assert market_share.company_country == test_countries[1]
    assert market_share.created_at is not None
    assert market_share.updated_at is not None
    assert str(market_share) == 'GOOGL'
    assert timezone.now() - market_share.updated_at < timezone.timedelta(seconds=1.5)

    for asset_type in market_share.assettypeassociation_set.all():
        assert asset_type.asset == market_share
        assert asset_type.asset_type == AssetType.objects.get(name='Share')
        assert asset_type.percentage == 1

@pytest.mark.django_db
def test_market_share_update_duplicate(test_countries, test_currencies, test_asset_types, test_exchange_marketes):

    MarketShare.objects.create(
        name='AAPL',
        code='AAPL',
        description='AAPL description',
        exchange_market=test_exchange_marketes[0],
        price_currency=test_currencies[0],
        company_country=test_countries[0])

    MarketShare.objects.create(
        name='GOOGL',
        code='GOOGL',
        description='GOOGL description',
        exchange_market=test_exchange_marketes[0],
        price_currency=test_currencies[1],
        company_country=test_countries[1])

    market_share = MarketShare.objects.get(name='AAPL')

    with pytest.raises(ValidationError) as exception_info:
        market_share.code = 'GOOGL'
        market_share.save()

    assert str(exception_info.value.error_dict.get('__all__')[0]) == "['Market asset with this Exchange market and Code already exists.']"
    assert MarketShare.objects.count() == 2

@pytest.mark.django_db
def test_market_share_update_blank_name(test_countries, test_currencies, test_asset_types, test_exchange_marketes):

    market_share = MarketShare.objects.create(
        name='AAPL',
        code='AAPL',
        description='AAPL description',
        exchange_market=test_exchange_marketes[0],
        price_currency=test_currencies[0],
        company_country=test_countries[0])

    with pytest.raises(ValidationError) as exception_info:
        market_share.name = ''
        market_share.save()

    assert str(exception_info.value.error_dict.get('name')[0]) == "['This field cannot be blank.']"
    assert MarketShare.objects.count() == 1

@pytest.mark.django_db
def test_market_share_update_name_too_long(test_countries, test_currencies, test_asset_types, test_exchange_marketes):

    market_share = MarketShare.objects.create(
        name='AAPL',
        code='AAPL',
        description='AAPL description',
        exchange_market=test_exchange_marketes[0],
        price_currency=test_currencies[0],
        company_country=test_countries[0])

    with pytest.raises(ValidationError) as exception_info:
        market_share.name = 'a' * 101
        market_share.save()

    assert str(exception_info.value.error_dict.get('name')[0]) == "['Ensure this value has at most 100 characters (it has 101).']"
    assert MarketShare.objects.count() == 1

@pytest.mark.django_db
def test_market_share_update_blank_code(test_countries, test_currencies, test_asset_types, test_exchange_marketes):

    market_share = MarketShare.objects.create(
        name='AAPL',
        code='AAPL',
        description='AAPL description',
        exchange_market=test_exchange_marketes[0],
        price_currency=test_currencies[0],
        company_country=test_countries[0])

    with pytest.raises(ValidationError) as exception_info:
        market_share.code = ''
        market_share.save()

    assert str(exception_info.value.error_dict.get('code')[0]) == "['This field cannot be blank.']"
    assert MarketShare.objects.count() == 1

@pytest.mark.django_db
def test_market_share_update_code_too_long(test_countries, test_currencies, test_asset_types, test_exchange_marketes):

    market_share = MarketShare.objects.create(
        name='AAPL',
        code='AAPL',
        description='AAPL description',
        exchange_market=test_exchange_marketes[0],
        price_currency=test_currencies[0],
        company_country=test_countries[0])

    with pytest.raises(ValidationError) as exception_info:
        market_share.code = 'a' * 101
        market_share.save()

    assert str(exception_info.value.error_dict.get('code')[0]) == "['Ensure this value has at most 100 characters (it has 101).']"
    assert MarketShare.objects.count() == 1

@pytest.mark.django_db
def test_market_share_update_too_long_description(test_countries, test_currencies, test_asset_types, test_exchange_marketes):

    market_share = MarketShare.objects.create(
        name='AAPL',
        code='AAPL',
        description='AAPL description',
        exchange_market=test_exchange_marketes[0],
        price_currency=test_currencies[0],
        company_country=test_countries[0])

    with pytest.raises(ValidationError) as exception_info:
        market_share.description = 'a' * 1001
        market_share.save()

    assert str(exception_info.value.error_dict.get('description')[0]) == "['Ensure this value has at most 1000 characters (it has 1001).']"
    assert MarketShare.objects.count() == 1

@pytest.mark.django_db
def test_market_share_update_no_exchange_market(test_countries, test_currencies, test_asset_types, test_exchange_marketes):

    market_share = MarketShare.objects.create(
        name='AAPL',
        code='AAPL',
        description='AAPL description',
        exchange_market=test_exchange_marketes[0],
        price_currency=test_currencies[0],
        company_country=test_countries[0])

    with pytest.raises(ValidationError) as exception_info:
        market_share.exchange_market = None
        market_share.save()

    assert str(exception_info.value.error_dict.get('exchange_market')[0]) == "['This field cannot be null.']"
    assert MarketShare.objects.count() == 1

@pytest.mark.django_db
def test_market_share_update_no_price_currency(test_countries, test_exchange_marketes, test_currencies, test_asset_types):

    market_share = MarketShare.objects.create(
        name='AAPL',
        code='AAPL',
        description='AAPL description',
        exchange_market=test_exchange_marketes[0],
        price_currency=test_currencies[0],
        company_country=test_countries[0])

    with pytest.raises(ValidationError) as exception_info:
        market_share.price_currency = None
        market_share.save()

    assert str(exception_info.value.error_dict.get('price_currency')[0]) == "['This field cannot be null.']"
    assert MarketShare.objects.count() == 1

@pytest.mark.django_db
def test_market_share_update_no_company_country(test_countries, test_currencies, test_exchange_marketes, test_asset_types):
    
    market_share = MarketShare.objects.create(
        name='AAPL',
        code='AAPL',
        description='AAPL description',
        exchange_market=test_exchange_marketes[0],
        price_currency=test_currencies[0],
        company_country=test_countries[0])

    with pytest.raises(ValidationError) as exception_info:
        market_share.company_country = None
        market_share.save()

    assert str(exception_info.value.error_dict.get('company_country')[0]) == "['This field cannot be null.']"
    assert MarketShare.objects.count() == 1

@pytest.mark.django_db
def test_market_share_delete(test_countries, test_currencies, test_asset_types, test_exchange_marketes):

    market_share = MarketShare.objects.create(
        name='AAPL',
        code='AAPL',
        description='AAPL description',
        exchange_market=test_exchange_marketes[0],
        price_currency=test_currencies[0],
        company_country=test_countries[0])

    assert MarketShare.objects.count() == 1
    market_share.delete()

    assert MarketShare.objects.count() == 0
    assert AssetTypeAssociation.objects.count() == 0

@pytest.mark.django_db
def test_market_ETF_create(test_countries, test_currencies, test_asset_types, test_exchange_marketes):

    market_ETF = MarketETF.objects.create(
        name='AAPL',
        code='AAPL',
        description='AAPL description',
        exchange_market=test_exchange_marketes[0],
        price_currency=test_currencies[0],
        fund_country=test_countries[0],
        dividend_distribution = True,
        replication_method = 'Full replication',)
    
    assert MarketETF.objects.count() == 1
    assert MarketShare.objects.count() == 0

    market_ETF = MarketETF.objects.first()

    assert market_ETF.name == 'AAPL'
    assert market_ETF.code == 'AAPL'
    assert market_ETF.description == 'AAPL description'
    assert market_ETF.exchange_market == test_exchange_marketes[0]
    assert market_ETF.price_currency == test_currencies[0]
    assert market_ETF.fund_country == test_countries[0]
    assert market_ETF.is_share == False
    assert market_ETF.is_etf == True
    assert market_ETF.dividend_distribution == True
    assert market_ETF.replication_method == 'Full replication'
    assert market_ETF.created_at is not None
    assert market_ETF.updated_at is not None
    assert str(market_ETF) == 'AAPL'
    assert timezone.now() - market_ETF.created_at < timezone.timedelta(seconds=1.5)

    assert AssetTypeAssociation.objects.count() == 0

@pytest.mark.django_db
def test_market_ETF_create_and_add_single_asset_type(test_countries, test_currencies, test_asset_types, test_exchange_marketes):

    asset_type_to_add = AssetType.objects.create(name='Shares', description='Shares description')

    market_ETF = MarketETF.objects.create(
        name='AAPL',
        code='AAPL',
        description='AAPL description',
        exchange_market=test_exchange_marketes[0],
        price_currency=test_currencies[0],
        fund_country=test_countries[0],
        dividend_distribution = True,
        replication_method = 'Full replication',)


    AssetTypeAssociation.objects.create(asset=market_ETF, asset_type=asset_type_to_add, percentage=1)


    assert AssetTypeAssociation.objects.count() == 1
    for asset_type in market_ETF.assettypeassociation_set.all():

        assert asset_type.asset == market_ETF
        assert asset_type.asset_type == asset_type_to_add
        assert asset_type.percentage == 1

@pytest.mark.django_db
def test_market_ETF_create_and_add_multiple_asset_types(test_countries, test_currencies, test_asset_types, test_exchange_marketes):

    asset_type_to_add_1 = AssetType.objects.create(name='Shares', description='Shares description')
    asset_type_to_add_2 = AssetType.objects.create(name='Bonds', description='Bonds description')

    market_ETF = MarketETF.objects.create(
        name='AAPL',
        code='AAPL',
        description='AAPL description',
        exchange_market=test_exchange_marketes[0],
        price_currency=test_currencies[0],
        fund_country=test_countries[0],
        dividend_distribution = True,
        replication_method = 'Full replication',)

    AssetTypeAssociation.objects.create(asset=market_ETF, asset_type=asset_type_to_add_1, percentage=0.5)
    AssetTypeAssociation.objects.create(asset=market_ETF, asset_type=asset_type_to_add_2, percentage=0.5)

    assert AssetTypeAssociation.objects.count() == 2
    for asset_type in market_ETF.assettypeassociation_set.all():

        assert asset_type.asset == market_ETF
        assert asset_type.asset_type in [asset_type_to_add_1, asset_type_to_add_2]
        assert asset_type.percentage in [0.5, 0.5]

@pytest.mark.django_db
def test_market_ETF_create_add_two_times_one_asset_type(test_countries, test_currencies, test_asset_types, test_exchange_marketes):

    asset_type_to_add_1 = AssetType.objects.create(name='Shares', description='Shares description')
    asset_type_to_add_2 = AssetType.objects.create(name='Bonds', description='Bonds description')

    market_ETF = MarketETF.objects.create(
        name='AAPL',
        code='AAPL',
        description='AAPL description',
        exchange_market=test_exchange_marketes[0],
        price_currency=test_currencies[0],
        fund_country=test_countries[0],
        dividend_distribution = True,
        replication_method = 'Full replication',)

    AssetTypeAssociation.objects.create(asset=market_ETF, asset_type=asset_type_to_add_1, percentage=0.5)

    with pytest.raises(ValidationError) as exception_info:
        AssetTypeAssociation.objects.create(asset=market_ETF, asset_type=asset_type_to_add_1, percentage=0.2)

    assert str(exception_info.value.error_dict.get('__all__')[0]) == "['Asset type association with this Asset and Asset type already exists.']"
    assert AssetTypeAssociation.objects.count() == 1

@pytest.mark.django_db
def test_market_ETF_create_add_two_times_two_asset_types_percentage_sum_above_1(test_countries, test_currencies, test_asset_types, test_exchange_marketes):

    asset_type_to_add_1 = AssetType.objects.create(name='Shares', description='Shares description')
    asset_type_to_add_2 = AssetType.objects.create(name='Bonds', description='Bonds description')

    market_ETF = MarketETF.objects.create(
        name='AAPL',
        code='AAPL',
        description='AAPL description',
        exchange_market=test_exchange_marketes[0],
        price_currency=test_currencies[0],
        fund_country=test_countries[0],
        dividend_distribution = True,
        replication_method = 'Full replication',)

    AssetTypeAssociation.objects.create(asset=market_ETF, asset_type=asset_type_to_add_1, percentage=0.5)

    with pytest.raises(ValidationError) as exception_info:
        AssetTypeAssociation.objects.create(asset=market_ETF, asset_type=asset_type_to_add_2, percentage=0.6)

    assert str(exception_info.value.error_dict.get('__all__')[0]) == "['Total percentage must be 1. Current total is 1.10']"
    assert AssetTypeAssociation.objects.count() == 1


@pytest.mark.django_db
def test_market_ETF_create_blank_fund_country(test_currencies, test_exchange_marketes):

    with pytest.raises(ValidationError) as exception_info:
        MarketETF.objects.create(
            name='AAPL',
            code='AAPL',
            description='AAPL description',
            exchange_market=test_exchange_marketes[0],
            price_currency=test_currencies[0],
            dividend_distribution = True,
            replication_method = 'Full replication',)

    assert str(exception_info.value.error_dict.get('fund_country')[0]) == "['This field cannot be null.']"
    assert MarketETF.objects.count() == 0

@pytest.mark.django_db
def test_market_ETF_create_no_dividend_distribution(test_countries, test_currencies, test_exchange_marketes):


    new_etf = MarketETF.objects.create(
        name='AAPL',
        code='AAPL',
        description='AAPL description',
        exchange_market=test_exchange_marketes[0],
        price_currency=test_currencies[0],
        fund_country=test_countries[0],
        replication_method = 'Full replication',)

    assert new_etf.dividend_distribution == False

@pytest.mark.django_db
def test_market_ETF_create_no_replication_method(test_countries, test_currencies, test_exchange_marketes):

    with pytest.raises(ValidationError) as exception_info:
        MarketETF.objects.create(
            name='AAPL',
            code='AAPL',
            description='AAPL description',
            exchange_market=test_exchange_marketes[0],
            price_currency=test_currencies[0],
            fund_country=test_countries[0],
            dividend_distribution = True,)

    assert str(exception_info.value.error_dict.get('replication_method')[0]) == "['This field cannot be blank.']"
    assert MarketETF.objects.count() == 0

@pytest.mark.django_db
def test_market_ETF_replication_method_too_long(test_countries, test_currencies, test_exchange_marketes):

    with pytest.raises(ValidationError) as exception_info:
        MarketETF.objects.create(
            name='AAPL',
            code='AAPL',
            description='AAPL description',
            exchange_market=test_exchange_marketes[0],
            price_currency=test_currencies[0],
            fund_country=test_countries[0],
            dividend_distribution = True,
            replication_method = 'a' * 101,)

    assert str(exception_info.value.error_dict.get('replication_method')[0]) == "['Ensure this value has at most 100 characters (it has 101).']"
    assert MarketETF.objects.count() == 0

@pytest.mark.django_db
def test_market_ETF_update(test_countries, test_currencies, test_asset_types, test_exchange_marketes):

    market_ETF = MarketETF.objects.create(
        name='AAPL',
        code='AAPL',
        description='AAPL description',
        exchange_market=test_exchange_marketes[0],
        price_currency=test_currencies[0],
        fund_country=test_countries[0],
        dividend_distribution = True,
        replication_method = 'Full replication',)

    market_ETF.name = 'GOOGL'
    market_ETF.code = 'GOOGL'
    market_ETF.description = 'GOOGL description'
    market_ETF.exchange_market = test_exchange_marketes[1]
    market_ETF.price_currency = test_currencies[1]
    market_ETF.fund_country = test_countries[1]
    market_ETF.dividend_distribution = False
    market_ETF.replication_method = 'Sampling'
    market_ETF.save()

    assert MarketETF.objects.count() == 1

    market_ETF = MarketETF.objects.first()

    assert market_ETF.name == 'GOOGL'
    assert market_ETF.code == 'GOOGL'
    assert market_ETF.description == 'GOOGL description'
    assert market_ETF.exchange_market == test_exchange_marketes[1]
    assert market_ETF.price_currency == test_currencies[1]
    assert market_ETF.fund_country == test_countries[1]
    assert market_ETF.dividend_distribution == False
    assert market_ETF.replication_method == 'Sampling'
    assert market_ETF.created_at is not None
    assert market_ETF.updated_at is not None
    assert str(market_ETF) == 'GOOGL'
    assert timezone.now() - market_ETF.updated_at < timezone.timedelta(seconds=1.5)

    assert AssetTypeAssociation.objects.count() == 0

@pytest.mark.django_db
def test_market_ETF_update_duplicate(test_countries, test_currencies, test_asset_types, test_exchange_marketes):

    MarketETF.objects.create(
        name='AAPL',
        code='AAPL',
        description='AAPL description',
        exchange_market=test_exchange_marketes[0],
        price_currency=test_currencies[0],
        fund_country=test_countries[0],
        dividend_distribution = True,
        replication_method = 'Full replication',)

    MarketETF.objects.create(
        name='GOOGL',
        code='GOOGL',
        description='GOOGL description',
        exchange_market=test_exchange_marketes[0],
        price_currency=test_currencies[1],
        fund_country=test_countries[1],
        dividend_distribution = False,
        replication_method = 'Sampling',)

    market_ETF = MarketETF.objects.get(name='AAPL')

    with pytest.raises(ValidationError) as exception_info:
        market_ETF.code = 'GOOGL'
        market_ETF.save()

    assert str(exception_info.value.error_dict.get('__all__')[0]) == "['Market asset with this Exchange market and Code already exists.']"
    assert MarketETF.objects.count() == 2

@pytest.mark.django_db
def test_market_ETF_update_no_fund_country(test_countries, test_currencies, test_asset_types, test_exchange_marketes):

    market_ETF = MarketETF.objects.create(
        name='AAPL',
        code='AAPL',
        description='AAPL description',
        exchange_market=test_exchange_marketes[0],
        price_currency=test_currencies[0],
        fund_country=test_countries[0],
        dividend_distribution = True,
        replication_method = 'Full replication',)

    with pytest.raises(ValidationError) as exception_info:
        market_ETF.fund_country = None
        market_ETF.save()

    assert str(exception_info.value.error_dict.get('fund_country')[0]) == "['This field cannot be null.']"
    assert MarketETF.objects.count() == 1

@pytest.mark.django_db
def test_market_ETF_update_no_dividend_distribution(test_countries, test_currencies, test_asset_types, test_exchange_marketes):

    market_ETF = MarketETF.objects.create(
        name='AAPL',
        code='AAPL',
        description='AAPL description',
        exchange_market=test_exchange_marketes[0],
        dividend_distribution=True,
        price_currency=test_currencies[0],
        fund_country=test_countries[0],
        replication_method = 'Full replication',)

    with pytest.raises(ValidationError) as exception_info:
        market_ETF.dividend_distribution = None
        market_ETF.save()

    assert str(exception_info.value.error_dict.get('dividend_distribution')[0]) == "['“None” value must be either True or False.']"

    assert MarketETF.objects.count() == 1


@pytest.mark.django_db
def test_market_ETF_update_no_replication_method(test_countries, test_currencies, test_asset_types, test_exchange_marketes):

    market_ETF = MarketETF.objects.create(
        name='AAPL',
        code='AAPL',
        description='AAPL description',
        exchange_market=test_exchange_marketes[0],
        dividend_distribution=True,
        price_currency=test_currencies[0],
        fund_country=test_countries[0],
        replication_method = 'Full replication',)

    with pytest.raises(ValidationError) as exception_info:
        market_ETF.replication_method = None
        market_ETF.save()

    assert str(exception_info.value.error_dict.get('replication_method')[0]) == "['This field cannot be null.']"
    assert MarketETF.objects.count() == 1

@pytest.mark.django_db
def test_market_ETF_update_replication_method_too_long(test_countries, test_currencies, test_asset_types, test_exchange_marketes):

    market_ETF = MarketETF.objects.create(
        name='AAPL',
        code='AAPL',
        description='AAPL description',
        exchange_market=test_exchange_marketes[0],
        dividend_distribution=True,
        price_currency=test_currencies[0],
        fund_country=test_countries[0],
        replication_method = 'Full replication',)

    with pytest.raises(ValidationError) as exception_info:
        market_ETF.replication_method = 'a' * 101
        market_ETF.save()

    assert str(exception_info.value.error_dict.get('replication_method')[0]) == "['Ensure this value has at most 100 characters (it has 101).']"
    assert MarketETF.objects.count() == 1

@pytest.mark.django_db
def test_market_ETF_delete(test_countries, test_currencies, test_asset_types, test_exchange_marketes):

    market_ETF = MarketETF.objects.create(
        name='AAPL',
        code='AAPL',
        description='AAPL description',
        exchange_market=test_exchange_marketes[0],
        dividend_distribution=True,
        price_currency=test_currencies[0],
        fund_country=test_countries[0],
        replication_method = 'Full replication',)

    assert MarketETF.objects.count() == 1

    #make asset type association
    new_asset_type = AssetType.objects.create(name='ETF2', description='ETF description')
    AssetTypeAssociation.objects.create(asset=market_ETF, asset_type=new_asset_type, percentage=1)
    assert AssetTypeAssociation.objects.count() == 1

    market_ETF.delete()

    assert MarketETF.objects.count() == 0
    assert AssetTypeAssociation.objects.count() == 0

