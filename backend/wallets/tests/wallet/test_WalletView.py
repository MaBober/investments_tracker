import pytest
from zoneinfo import ZoneInfo
from unittest import (
    mock,
)  # adding it here just to show you. Always define imports at file top level
from wallets.tests.test_fixture import api_client, test_user
from wallets.tests.wallet.test_fixture import test_wallets, test_wallets_data
from wallets.schema.wallet import ListWalletsRequest, ListWalletsResponse
from rest_framework.request import Request


class TestWalletAPI:

    @pytest.mark.django_db
    @mock.patch("wallets.controllers.wallet.WalletController.list_wallets")
    def test_get_success(self, list_wallets_mock, api_client, test_user, test_wallets):

        expected_response = [
            {
                "id": test_wallets[0].id,
                "name": test_wallets[0].name,
                "description": test_wallets[0].description,
                "owner_id": test_wallets[0].owner.id,
                "co_owners": [
                    co_owner.id for co_owner in test_wallets[0].co_owners.all()
                ],
                'current_value': '0.00',
                'created_at': test_wallets[0].created_at.astimezone(ZoneInfo('Europe/Warsaw')).isoformat(),
                'updated_at': test_wallets[0].updated_at.astimezone(ZoneInfo('Europe/Warsaw')).isoformat()


            },
            {
                "id": test_wallets[1].id,
                "name": test_wallets[1].name,
                "description": test_wallets[1].description,
                "owner_id": test_wallets[1].owner.id,
                "co_owners": [
                    co_owner.id for co_owner in test_wallets[1].co_owners.all()
                ],
                'current_value': '0.00',
                'created_at': test_wallets[1].created_at.astimezone(ZoneInfo('Europe/Warsaw')).isoformat(),
                'updated_at': test_wallets[1].updated_at.astimezone(ZoneInfo('Europe/Warsaw')).isoformat()
            },
        ]

        list_wallets_mock.return_value = ListWalletsResponse(
            wallets=[test_wallets[0], test_wallets[1]]
        )

        api_client.force_authenticate(user=test_user[0])
        response = api_client.get(api_client.url + "wallets/")

        assert response.json() == expected_response
        assert response.status_code == 200
        list_wallets_mock.assert_called_once()
        

    @pytest.mark.django_db
    @mock.patch("wallets.controllers.wallet.WalletController.list_wallets")
    def test_get_no_wallets(self, list_wallets_mock, api_client, test_user):

        list_wallets_mock.return_value = ListWalletsResponse(wallets=[])

        api_client.force_authenticate(user=test_user[0])
        response = api_client.get(api_client.url + "wallets/")

        assert response.json() == []
        assert response.status_code == 200
        list_wallets_mock.assert_called_once()



