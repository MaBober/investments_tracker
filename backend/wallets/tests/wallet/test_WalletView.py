from django.http import QueryDict
import pytest

from unittest import mock

from wallets.schema.wallet import ListWalletsRequest, ListWalletsResponse
from wallets.serializers.wallet import WalletListParametersSerializer

from wallets.tests.test_fixture import api_client, test_user


class TestWalletAPI:

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "expected_response, query_params",
        [
            ([],{}),
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
                    "created_after": "2024-06-03"
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
        query_params_check = QueryDict('', mutable=True)
        query_params_check.update(query_params)

        serialized_query_params = WalletListParametersSerializer(data=query_params_check)
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
            (
                {"owner_id": "1, a"}
            ),
            (
                {"co_owner_id": "1, a"}
            ),
            (
                {"created_before": "2024-06-32"}
            ),
            (
                {"created_after": "2024-06-32"}
            )
        ]
    )
    def test_get_fail(self, query_params, api_client, test_user):

        api_client.force_authenticate(user=test_user[0])
        response = api_client.get(api_client.url + "wallets/", query_params)

        assert response.status_code == 400
        