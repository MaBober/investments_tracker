from django.http import QueryDict
from django.contrib.auth.models import User
import pytest

from unittest import mock

from wallets.schema.wallet import (
    ListWalletsRequest,
    ListWalletsResponse,
    BuildWalletRequest,
    BuildWalletResponse,
)
from wallets.serializers.wallet import WalletListParametersSerializer

from wallets.tests.test_fixture import api_client, test_user
from wallets.tests.wallet.test_fixture import test_wallets, test_wallets_data


class TestWalletAPI:

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "expected_response, query_params",
        [
            ([], {}),
            (
                [
                    {
                        "id": 1,
                        "name": "John Wallet",
                        "description": "John Wallet description",
                        "owner_id": 1,
                        "co_owners": [],
                        "current_value": "0.00",
                        "created_at": "2021-10-10T12:00:00+02:00",
                        "updated_at": "2021-10-10T12:00:00+02:00",
                    },
                    {
                        "id": 2,
                        "name": "Paul Wallet",
                        "description": "Paul Wallet description",
                        "owner_id": 2,
                        "co_owners": [3],
                        "current_value": "0.00",
                        "created_at": "2021-10-10T12:00:00+02:00",
                        "updated_at": "2021-10-10T12:00:00+02:00",
                    },
                ],
                {
                    "owner_id": "1,2",
                    "co_owner_id": "3",
                    "created_before": "2024-06-12",
                    "created_after": "2024-06-03",
                },
            ),
        ],
    )
    @mock.patch("wallets.controllers.wallet.WalletController.list_wallets")
    def test_get_success(
        self, list_wallets_mock, expected_response, query_params, api_client, test_user
    ):

        list_wallets_mock.return_value = ListWalletsResponse(data=expected_response)

        api_client.force_authenticate(user=test_user[0])
        response = api_client.get(api_client.url + "wallets/", query_params)

        assert response.json() == expected_response
        assert response.status_code == 200

        # This step simulates the parameter processing as it would occur in the actual view,
        # ensuring the mock is called with accurately transformed and validated parameters.
        query_params_check = QueryDict("", mutable=True)
        query_params_check.update(query_params)

        serialized_query_params = WalletListParametersSerializer(
            data=query_params_check
        )
        serialized_query_params.is_valid(raise_exception=True)

        list_wallets_mock.assert_called_once()
        list_wallets_mock.assert_called_with(
            ListWalletsRequest(
                query_parameters=serialized_query_params.validated_data,
                user_id=test_user[0].id,
                user_is_staff=False,
            )
        )

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "query_params",
        [
            ({"owner_id": "1, a"}),
            ({"co_owner_id": "1, a"}),
            ({"created_before": "2024-06-32"}),
            ({"created_after": "2024-06-32"}),
        ],
    )
    @mock.patch("wallets.controllers.wallet.WalletController.list_wallets")
    def test_get_fail(self, list_wallets_mock, query_params, api_client, test_user):

        api_client.force_authenticate(user=test_user[0])
        response = api_client.get(api_client.url + "wallets/", query_params)

        list_wallets_mock.assert_not_called()
        assert response.status_code == 400

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "request_data, expected_response",
        [
            (
                {
                    "name": "John Wallet",
                    "description": "John Wallet description",
                    "co_owners": [],
                },
                {
                    "id": 1,
                    "name": "John Wallet",
                    "description": "John Wallet description",
                    "owner_id": 1,
                    "co_owners": [],
                    "current_value": "0.00",
                    "created_at": "2021-10-10T12:00:00+02:00",
                    "updated_at": "2021-10-10T12:00:00+02:00",
                },
            ),
            (
                {
                    "name": "Paul Wallet",
                    "description": "Paul Wallet description",
                    "co_owners": ["placeholder_id"],
                },
                {
                    "id": 2,
                    "name": "Paul Wallet",
                    "description": "Paul Wallet description",
                    "owner_id": 2,
                    "co_owners": ["placeholder_id"],
                    "current_value": "0.00",
                    "created_at": "2021-10-10T12:00:00+02:00",
                    "updated_at": "2021-10-10T12:00:00+02:00",
                },
            ),
        ],
    )
    @mock.patch("wallets.controllers.wallet.WalletController.build_wallet")
    def test_post_success(
        self, build_wallet_mock, request_data, expected_response, api_client, test_user
    ):

        # Prepare the mock response and request - replacing co_owner placeholder with existing ids
        if request_data.get("co_owners"):
            real_co_owners = []
            for i, co_owner in enumerate(request_data.get("co_owners", [])):
                real_co_owners.append(test_user[i + 1].id)

            expected_response["co_owners"] = real_co_owners
            request_data["co_owners"] = real_co_owners

        build_wallet_mock.return_value = BuildWalletResponse(
            data=expected_response,
            location=api_client.url + f"wallets/{expected_response['id']}/",
        )

        api_client.force_authenticate(user=test_user[0])
        response = api_client.post(api_client.url + "wallets/", request_data)

        assert response.json() == expected_response
        assert response.status_code == 201
        assert (
            response.headers["Location"]
            == api_client.url + f"wallets/{expected_response['id']}/"
        )

        # This step simulates the parameter processing as it would occur in the actual view,
        # ensuring the mock is called with accurately transformed and validated parameters

        co_owner_instance = []
        for co_owner in request_data.get("co_owners", []):
            co_owner_instance.append(User.objects.get(id=co_owner))

        request_data["co_owners"] = co_owner_instance

        build_wallet_mock.assert_called_once()
        build_wallet_mock.assert_called_with(
            BuildWalletRequest(
                data=request_data,
                owner_id=test_user[0].id,
            )
        )

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "request_data",
        [
            ({"name": "XX"}),
            ({"name": ""}),
            ({"name": "x" * 101}),
            ({"description": "John Wallet description"}),
            ({"name": "My Wallet", "description": "x" * 1001}),
            ({"name": "My Wallet", "co_owners": [1000]}),
            ({"name": "My Wallet", "co_owners": ["xxx"]}),
            ({"name": "My Wallet", "co_owners": ["same_as_owner"]}),
        ],
    )
    @mock.patch("wallets.controllers.wallet.WalletController.build_wallet")
    def test_post_fail(self, build_wallet_mock, request_data, api_client, test_user):

        if request_data.get("co_owners") == ["same_as_owner"]:
            request_data["co_owners"] = [test_user[0].id]

        api_client.force_authenticate(user=test_user[0])
        response = api_client.post(api_client.url + "wallets/", request_data)

        build_wallet_mock.assert_not_called()
        assert response.status_code == 400

    @pytest.mark.django_db
    @mock.patch("wallets.controllers.wallet.WalletController.build_wallet")
    def test_post_fail_duplicated_name(
        self, build_wallet_mock, api_client, test_user, test_wallets
    ):

        for wallet in test_wallets:
            if wallet.owner == test_user[0]:
                request_data = {"name": wallet.name}

        api_client.force_authenticate(user=test_user[0])
        response = api_client.post(api_client.url + "wallets/", request_data)

        build_wallet_mock.assert_not_called()
        assert response.status_code == 400
