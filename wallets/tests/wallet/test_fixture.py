import pytest

from rest_framework.test import APIClient

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from wallets.models import Wallet

@pytest.fixture
def test_user():

    users = []
    users_data =[
        {'username': 'john', 'email': 'lennon@thebeatles.com', 'password': 'johnpassword'},
        {'username': 'paul', 'email': 'mccarthney@thebeatles.com', 'password': 'paulpassword'},
        {'username': 'george', 'email': 'harrison@thebeatles.com', 'password': 'georgepassword'},
        {'username': 'ringo', 'email': 'starr@thebeatles.com', 'password': 'ringopassword'}
    ]   

    for user in users_data:
        users.append(User.objects.create_user(user['username'], user['email'], user['password']))

    return users

@pytest.fixture
def api_client():

    client = APIClient()
    return client

@pytest.fixture
def authenticated_client(api_client, test_user):
    
    api_client.force_authenticate(user=test_user[0])
    #Set an url for the client
    api_client.url = '/api/v1/'
    return api_client


@pytest.fixture
def test_wallets(test_user):

    wallets = []
    wallets_data = [
        {'owner': test_user[0], 'name': 'John Wallet', 'description': 'John Wallet description'},
        {'owner': test_user[1], 'name': 'Paul Wallet', 'description': 'Paul Wallet description', 'co_owners': [test_user[0]]},
        {'owner': test_user[2], 'name': 'George Wallet', 'description': 'George Wallet description'},
        {'owner': test_user[3], 'name': 'Ringo Wallet', 'description': 'Ringo Wallet description'},
        {'owner': test_user[0], 'name': 'John Wallet 2', 'description': 'John Wallet 2 description'}
    ]

    for wallet in wallets_data:
        wallets.append(Wallet.objects.create(owner=wallet['owner'], name=wallet['name'], description=wallet['description']))
    
    return wallets


def api_url(url):
    return '/api/v1/' + url