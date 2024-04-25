import pytest

from rest_framework.test import APIClient

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from wallets.models import Wallet, Account, AccountType, AccountInstitution, AccountInstitutionType
from wallets.tests.test_fixture import test_user, test_countries, test_currencies
from wallets.tests.wallet.test_fixture import test_wallets

@pytest.fixture
def test_account_types():

    account_types = []
    account_types_data = [
        {'name': 'Checking', 'description': 'Checking account type'},
        {'name': 'Savings', 'description': 'Savings account type'},
        {'name': 'Credit', 'description': 'Credit account type'},
        {'name': 'Investment', 'description': 'Investment account type'},
        {'name': 'Retirement', 'description': 'Retirement account type'},
        {'name': 'Loan', 'description': 'Loan account type'},
        {'name': 'Other', 'description': 'Other account type'}
    ]

    for account_type in account_types_data:
        account_types.append(AccountType.objects.create(name=account_type['name'], description=account_type['description']))

    return account_types

@pytest.fixture
def test_account_institution_types():

    account_institution_types = []
    account_institution_types_data = [
        {'name': 'Bank', 'description': 'Bank account institution type'},
        {'name': 'Credit Union', 'description': 'Credit Union account institution type'},
        {'name': 'Brokerage', 'description': 'Brokerage account institution type'},
        {'name': 'Insurance', 'description': 'Insurance account institution type'},
        {'name': 'Other', 'description': 'Other account institution type'}
    ]

    for account_institution_type in account_institution_types_data:
        account_institution_types.append(AccountInstitutionType.objects.create(name=account_institution_type['name'], description=account_institution_type['description']))

    return account_institution_types

@pytest.fixture
def test_institution(test_account_institution_types, test_countries):

    institutions = []
    institutions_data = [
        {'name': 'Bank of America', 'type': test_account_institution_types[0], 'country': test_countries[0], 'description': 'Bank of America description'},
        {'name': 'Chase', 'type': test_account_institution_types[0], 'country': test_countries[0], 'description': 'Chase description'},
        {'name': 'Wells Fargo', 'type': test_account_institution_types[0], 'country': test_countries[0], 'description': 'Wells Fargo description'},
        {'name': 'USAA', 'type': test_account_institution_types[0], 'country': test_countries[0], 'description': 'USAA description'},
        {'name': 'Navy Federal Credit Union', 'type': test_account_institution_types[1], 'country': test_countries[0], 'description': 'Navy Federal Credit Union description'},
        {'name': 'Charles Schwab', 'type': test_account_institution_types[2], 'country': test_countries[0], 'description': 'Charles Schwab description'},
        {'name': 'Vanguard', 'type': test_account_institution_types[2], 'country': test_countries[0], 'description': 'Vanguard description'},
        {'name': 'Fidelity', 'type': test_account_institution_types[2], 'country': test_countries[0], 'description': 'Fidelity description'},
        {'name': 'State Farm', 'type': test_account_institution_types[3], 'country': test_countries[0], 'description': 'State Farm description'},
        {'name': 'Geico', 'type': test_account_institution_types[3], 'country': test_countries[0], 'description': 'Geico description'},
        {'name': 'Other', 'type': test_account_institution_types[4], 'country': test_countries[0], 'description': 'Other description'}
    ]

    for institution in institutions_data:
        institutions.append(AccountInstitution.objects.create(name=institution['name'], type=institution['type'], country=institution['country'], description=institution['description']))

    return institutions

@pytest.fixture
def test_accounts(test_account_types, test_institution, test_wallets, test_user, test_currencies):

    accounts = []
    accounts_data = [
        {'name': 'Checking Account', 'type': test_account_types[0], 'institution': test_institution[0], 'wallets': [test_wallets[0]], 'description': 'Checking account description', "owner": test_user[0], "currency": [test_currencies[0]], "co_owners": [test_user[1], test_user[2]]},
        {'name': 'Savings Account', 'type': test_account_types[1], 'institution': test_institution[1], 'wallets': [test_wallets[1]], 'description': 'Savings account description', "owner": test_user[1], "currency": [test_currencies[0]], "co_owners": [test_user[2]]},
        {'name': 'Credit Card', 'type': test_account_types[2], 'institution': test_institution[2], 'wallets': [test_wallets[2]], 'description': 'Credit card description', "owner": test_user[2], "currency": [test_currencies[0]], "co_owners": [test_user[1]]},
        {'name': 'Investment Account', 'type': test_account_types[3], 'institution': test_institution[3], 'wallets': [test_wallets[3]], 'description': 'Investment account description', "owner": test_user[3], "currency": [test_currencies[0]], "co_owners": [test_user[1]]},
        {'name': 'Retirement Account', 'type': test_account_types[4], 'institution': test_institution[4], 'wallets': [test_wallets[0]], 'description': 'Retirement account description', "owner": test_user[0], "currency": [test_currencies[0]], "co_owners": [test_user[1]]},
        {'name': 'Loan Account', 'type': test_account_types[5], 'institution': test_institution[5], 'wallets': [test_wallets[0]], 'description': 'Loan account description', "owner": test_user[0], "currency": [test_currencies[0]], "co_owners": [test_user[1]]},
        {'name': 'Other Account', 'type': test_account_types[6], 'institution': test_institution[6], 'wallets': [test_wallets[0]], 'description': 'Other account description', "owner": test_user[0], "currency": [test_currencies[0]], "co_owners": [test_user[1]]}
    ]


    for account in accounts_data:
        accounts.append(Account.objects.create(owner=account['owner'] , name=account['name'], type=account['type'], institution=account['institution'], description=account['description']))
        accounts[-1].wallets.set(account['wallets'])
        accounts[-1].co_owners.set(account['co_owners'])
        accounts[-1].currencies.set(account['currency'])


    return accounts