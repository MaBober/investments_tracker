from ast import List
from math import exp
import pytest
from unittest.mock import patch, MagicMock

from django.conf import settings

from wallets.models import Wallet
from wallets.controllers.wallet import WalletController
from wallets.schema.wallet import (
    BuildWalletRequest,
    BuildWalletResponse,
    ListWalletsRequest,
    ListWalletsResponse,
    WalletDetailsResponse,
    WalletDetailsRequest,
    UpdateWalletRequest,
    UpdateWalletResponse,
    DeleteWalletRequest,
    DeleteWalletResponse,
)

from wallets.tests.test_fixture import test_user
from wallets.tests.wallet.test_fixture import single_wallet


@pytest.mark.django_db
@patch("wallets.repository.wallet.WalletRepository.create_wallet")
@patch("wallets.repository.wallet.WalletRepository.add_co_owners_to_wallet")
def test_build_wallet_with_co_owner(
    add_co_owners_to_wallet_mock, mock_create_wallet, test_user, single_wallet
):
    mock_wallet = single_wallet
    mock_wallet.co_owners = [test_user[1]]

    mock_create_wallet.return_value = mock_wallet

    response = WalletController.build_wallet(
        BuildWalletRequest(
            data={
                "name": mock_wallet.name,
                "description": mock_wallet.description,
                "co_owners": mock_wallet.co_owners,
            },
            owner_id=test_user[0].id,
        )
    )

    expected_response = BuildWalletResponse(
        data={
            "id": 1,
            "name": mock_wallet.name,
            "owner_id": test_user[0].id,
            "co_owners": [co_owner.id for co_owner in mock_wallet.co_owners],
            "description": mock_wallet.description,
        },
        status=201,
        location=f"{settings.API_ROOT_PATH}wallets/{mock_wallet.id}",
    )

    assert response == expected_response
    mock_create_wallet.assert_called_once()
    mock_create_wallet.assert_called_with(
        request_data={
            "name": mock_wallet.name,
            "description": mock_wallet.description,
        },
        owner_id=test_user[0].id,
    )
    add_co_owners_to_wallet_mock.assert_called_once()


@pytest.mark.django_db
@patch("wallets.repository.wallet.WalletRepository.create_wallet")
@patch("wallets.repository.wallet.WalletRepository.add_co_owners_to_wallet")
def test_build_wallet_without_co_owner(
    add_co_owners_to_wallet_mock, mock_create_wallet, test_user, single_wallet
):

    mock_wallet = single_wallet

    mock_create_wallet.return_value = mock_wallet

    response = WalletController.build_wallet(
        BuildWalletRequest(
            data={"name": mock_wallet.name, "description": mock_wallet.description},
            owner_id=test_user[0].id,
        )
    )

    expected_response = BuildWalletResponse(
        data={
            "id": 1,
            "name": mock_wallet.name,
            "owner_id": test_user[0].id,
            "co_owners": [],
            "description": mock_wallet.description,
        },
        status=201,
        location=f"{settings.API_ROOT_PATH}wallets/{mock_wallet.id}",
    )

    assert response == expected_response
    mock_create_wallet.assert_called_once()
    mock_create_wallet.assert_called_with(
        request_data={
            "name": mock_wallet.name,
            "description": mock_wallet.description,
        },
        owner_id=test_user[0].id,
    )
    add_co_owners_to_wallet_mock.assert_not_called()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "is_admin, query_params, expected_call_args",
    [
        (
            False,
            {},
            {
                "user_id": "test_user_id",
                "co_owner_id": None,
                "owner_id": None,
                "created_before": None,
                "created_after": None,
            },
        ),
        (
            True,
            {},
            {
                "user_id": None,
                "co_owner_id": None,
                "owner_id": None,
                "created_before": None,
                "created_after": None,
            },
        ),
        (
            True,
            {
                "owner_id": "test_user_id",
                "co_owner_id": "test_user_co_id",
                "created_before": "2022-10-10T10:10:10.000000Z",
                "created_after": "2021-10-10T10:10:10.000000Z",
            },
            {
                "user_id": None,
                "co_owner_id": "test_user_co_id",
                "owner_id": "test_user_id",
                "created_before": "2022-10-10T10:10:10.000000Z",
                "created_after": "2021-10-10T10:10:10.000000Z",
            },
        ),
    ],
)
@patch("wallets.repository.wallet.WalletRepository.get_all_wallets")
def test_list_wallets(
    get_all_wallets_mock,
    test_user,
    single_wallet,
    is_admin,
    query_params,
    expected_call_args,
):

    mock_wallet = single_wallet

    get_all_wallets_mock.return_value = [mock_wallet]

    response = WalletController.list_wallets(
        ListWalletsRequest(
            query_parameters=query_params,
            user_id=test_user[0].id,
            user_is_staff=is_admin,
        )
    )

    expected_response = ListWalletsResponse(
        data=[
            {
                "id": 1,
                "owner_id": test_user[0].id,
                "co_owners": [],
                "name": mock_wallet.name,
                "description": mock_wallet.description,
                "created_at": mock_wallet.created_at,
                "updated_at": mock_wallet.updated_at,
                "current_value": "101.00",
            }
        ],
        status=200,
    )

    assert response == expected_response
    get_all_wallets_mock.assert_called_once()

    if expected_call_args.get("user_id"):
        expected_call_args["user_id"] = test_user[0].id
    get_all_wallets_mock.assert_called_with(**expected_call_args)


@pytest.mark.django_db
@patch("wallets.repository.wallet.WalletRepository.get_single_wallet")
def test_get_wallet_details(get_single_wallet_mock, test_user, single_wallet):

    mock_wallet = single_wallet

    get_single_wallet_mock.return_value = mock_wallet

    response = WalletController.wallet_details(WalletDetailsRequest(pk=mock_wallet.id))

    expected_response = WalletDetailsResponse(
        data={
            "id": 1,
            "owner_id": test_user[0].id,
            "co_owners": [],
            "name": mock_wallet.name,
            "description": mock_wallet.description,
            "created_at": mock_wallet.created_at,
            "updated_at": mock_wallet.updated_at,
            "current_value": "101.00",
        },
        status=200,
    )

    assert response == expected_response
    get_single_wallet_mock.assert_called_once()
    get_single_wallet_mock.assert_called_with(1)


@pytest.mark.django_db
@patch("wallets.repository.wallet.WalletRepository.get_single_wallet")
def test_get_wallet_details_with_no_wallet(get_single_wallet_mock, test_user):

    get_single_wallet_mock.return_value = None

    response = WalletController.wallet_details(WalletDetailsRequest(pk=1))

    expected_response = WalletDetailsResponse(data={}, status=200)

    assert response == expected_response
    get_single_wallet_mock.assert_called_once()
    get_single_wallet_mock.assert_called_with(1)


@pytest.mark.django_db
@patch("wallets.repository.wallet.WalletRepository.get_single_wallet")
@patch("wallets.repository.wallet.WalletRepository.save_wallet")
@patch("wallets.repository.wallet.WalletRepository.add_co_owners_to_wallet")
@patch("wallets.repository.wallet.WalletRepository.erase_co_owners_from_wallet")
def test_update_wallet(
    erase_co_owners_from_wallet_mock,
    add_co_owners_to_wallet_mock,
    save_wallet_mock,
    get_single_wallet_mock,
    test_user,
    single_wallet,
):

    mock_wallet = single_wallet
    mock_wallet.co_owners = []

    get_single_wallet_mock.return_value = mock_wallet

    response = WalletController.update_wallet(
        UpdateWalletRequest(
            pk=mock_wallet.id,
            data={"name": "Updated Wallet", "description": "Updated description"},
        )
    )

    expected_response = UpdateWalletResponse(
        data={
            "id": 1,
            "owner_id": test_user[0].id,
            "co_owners": [],
            "name": "Updated Wallet",
            "description": "Updated description",
        },
        status=201,
    )

    assert response == expected_response
    get_single_wallet_mock.assert_called_once()
    get_single_wallet_mock.assert_called_with(1)
    save_wallet_mock.assert_called_once()
    save_wallet_mock.assert_called_with(mock_wallet)
    add_co_owners_to_wallet_mock.assert_not_called()
    erase_co_owners_from_wallet_mock.assert_called_once()

    assert mock_wallet.name == "Updated Wallet"
    assert mock_wallet.description == "Updated description"


@pytest.mark.django_db
@patch("wallets.repository.wallet.WalletRepository.get_single_wallet")
@patch("wallets.repository.wallet.WalletRepository.save_wallet")
@patch("wallets.repository.wallet.WalletRepository.add_co_owners_to_wallet")
@patch("wallets.repository.wallet.WalletRepository.erase_co_owners_from_wallet")
def test_update_wallet_with_co_owners(
    erase_co_owners_from_wallet_mock,
    add_co_owners_to_wallet_mock,
    save_wallet_mock,
    get_single_wallet_mock,
    test_user,
    single_wallet,
):

    mock_wallet = single_wallet
    mock_wallet.co_owners = [test_user[1]]

    get_single_wallet_mock.return_value = mock_wallet

    response = WalletController.update_wallet(
        UpdateWalletRequest(
            pk=mock_wallet.id,
            data={
                "name": "Updated Wallet",
                "description": "Updated description",
                "co_owners": [test_user[1].id],
            },
        )
    )

    expected_response = UpdateWalletResponse(
        data={
            "id": 1,
            "owner_id": test_user[0].id,
            "co_owners": [test_user[1].id],
            "name": "Updated Wallet",
            "description": "Updated description",
        },
        status=201,
    )

    assert response == expected_response
    get_single_wallet_mock.assert_called_once()
    get_single_wallet_mock.assert_called_with(1)
    save_wallet_mock.assert_called_once()
    save_wallet_mock.assert_called_with(mock_wallet)
    add_co_owners_to_wallet_mock.assert_called_once()
    erase_co_owners_from_wallet_mock.assert_not_called()

    assert mock_wallet.name == "Updated Wallet"
    assert mock_wallet.description == "Updated description"
    assert mock_wallet.co_owners == [test_user[1]]


@pytest.mark.django_db
@patch("wallets.repository.wallet.WalletRepository.get_single_wallet")
@patch("wallets.repository.wallet.WalletRepository.delete_wallet")
def test_delete_wallet(
    delete_wallet_mock, get_single_wallet_mock, test_user, single_wallet
):

    mock_wallet = single_wallet

    get_single_wallet_mock.return_value = mock_wallet

    response = WalletController.delete_wallet(DeleteWalletRequest(pk=mock_wallet.id))

    expected_response = DeleteWalletResponse()

    assert response == expected_response
    get_single_wallet_mock.assert_called_once()
    get_single_wallet_mock.assert_called_with(1)
    delete_wallet_mock.assert_called_once()
    delete_wallet_mock.assert_called_with(mock_wallet)
