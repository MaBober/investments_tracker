import pytest

from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Count


from wallets.models import Wallet, Account, Deposit

from wallets.tests.test_fixture import test_user, test_currencies, test_countries
from wallets.tests.wallet.test_fixture import test_wallets
from wallets.tests.account.test_fixture import test_accounts, test_account_types, test_account_institution_types, test_institution
