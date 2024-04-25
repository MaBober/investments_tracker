import pytest

from rest_framework.test import APIClient

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from wallets.models import Country, Currency
from wallets.models import Wallet
from wallets.models import Account, AccountType, AccountInstitution, AccountInstitutionType


@pytest.fixture
def test_user():

    users = []
    users_data =[
        {'username': 'john', 'email': 'lennon@thebeatles.com', 'password': 'johnpassword'},
        {'username': 'paul', 'email': 'mccarthney@thebeatles.com', 'password': 'paulpassword'},
        {'username': 'george', 'email': 'harrison@thebeatles.com', 'password': 'georgepassword'},
        {'username': 'ringo', 'email': 'starr@thebeatles.com', 'password': 'ringopassword'},
        {'username': 'admin', 'email': 'admin@admin.pl', 'password': 'adminpassword', 'is_staff': True, 'is_superuser': True}
    ]   

    for user in users_data:
        users.append(User.objects.create_user(user['username'], user['email'], user['password']))
        if 'is_staff' in user:
            users[-1].is_staff = user['is_staff']
        if 'is_superuser' in user:
            users[-1].is_superuser = user['is_superuser']

    return users

@pytest.fixture
def test_countries():

    countries = []
    countries_data = [
        {'name': 'Poland', 'code': 'PL'},
        {'name': 'United States', 'code': 'US'},
        {'name': 'Germany', 'code': 'DE'},
        {'name': 'France', 'code': 'FR'},
        {'name': 'United Kingdom', 'code': 'UK'},
        {'name': 'Switzerland', 'code': 'CH'}
    ]

    for country in countries_data:
        countries.append(Country.objects.create(name=country['name'], code=country['code']))

    return countries

@pytest.fixture
def test_currencies(test_countries):

    currencies = []
    currencies_data = [
        {'name': 'Polish Zloty', 'code': 'PLN', 'symbol': 'zł', 'country': 'Poland'},
        {'name': 'US Dollar', 'code': 'USD', 'symbol': '$', 'country': 'United States'},
        {'name': 'Euro', 'code': 'EUR', 'symbol': '€', 'country': ['Germany', 'France']},
        {'name': 'British Pound', 'code': 'GBP', 'symbol': '£', 'country': 'United Kingdom'},
        {'name': 'Swiss Franc', 'code': 'CHF', 'symbol': 'CHF', 'country': 'Switzerland'}
    ]

    for currency in currencies_data:
        currencies.append(Currency.objects.create(name=currency['name'], code=currency['code'], symbol=currency['symbol']))
        if type(currency['country']) == str:
            currencies[-1].countries.add(Country.objects.get(name=currency['country']))
        else:
            for country in currency['country']:
                currencies[-1].countries.add(Country.objects.get(name=country))

    return currencies

@pytest.fixture
def api_client():

    client = APIClient()
    client.url = '/api/v1/'
    return client

@pytest.fixture
def authenticated_client(api_client, test_user):
    
    api_client.force_authenticate(user=test_user[0])
    #Set an url for the client
    # api_client.url = '/api/v1/'
    return api_client

@pytest.fixture
def admin_logged_client(api_client, test_user):

    api_client.force_authenticate(user=test_user[4])

    return api_client

def api_url(url):
    return '/api/v1/' + url