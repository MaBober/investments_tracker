import pytest
from unittest.mock import MagicMock

from wallets.models import Wallet


@pytest.fixture
def test_wallets_data(test_user):

    wallets_data = [
        {
            "owner": test_user[0],
            "name": "John Wallet",
            "description": "John Wallet description",
        },
        {
            "owner": test_user[1],
            "name": "Paul Wallet",
            "description": "Paul Wallet description",
            "co_owners": [test_user[2]],
        },
        {
            "owner": test_user[2],
            "name": "George Wallet",
            "description": "George Wallet description",
        },
        {
            "owner": test_user[3],
            "name": "Ringo Wallet",
            "description": "Ringo Wallet description",
        },
        {
            "owner": test_user[0],
            "name": "John Wallet 2",
            "description": "John Wallet 2 description",
        },
    ]

    return wallets_data


@pytest.fixture
def single_wallet(test_user):

    mock_wallet = MagicMock(spec=Wallet)
    mock_wallet.id = 1
    mock_wallet.name = "TestWallet"
    mock_wallet.owner = test_user[0]
    mock_wallet.owner_id = test_user[0].id
    mock_wallet.co_owners = []
    mock_wallet.description = "Test description"
    mock_wallet.created_at = "2021-10-10T10:10:10.000000Z"
    mock_wallet.updated_at = "2022-10-10T10:10:10.000000Z"
    mock_wallet.current_value = 101

    return mock_wallet


@pytest.fixture
def test_wallets(test_wallets_data):

    wallets = []
    wallets_data = test_wallets_data

    for wallet in wallets_data:
        wallets.append(
            Wallet.objects.create(
                owner=wallet["owner"],
                name=wallet["name"],
                description=wallet["description"],
            )
        )
        if "co_owners" in wallet:
            wallets[-1].co_owners.set(wallet["co_owners"])

    return wallets
