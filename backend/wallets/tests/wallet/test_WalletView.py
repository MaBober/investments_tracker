import pytest
from unittest import mock # adding it here just to show you. Always define imports at file top level
from wallets.tests.test_fixture import authenticated_client, api_client, test_user
from wallets.controllers.wallet import WalletController
from wallets.schema.wallet import ListWalletsRequest, ListWalletsResponse


class TestWalletAPI:
    
    # @mock.patch('wallets.controllers.wallet.WalletController.list_wallets')
    #@mock.patch("path to WalletController.list_wallets", return_value=mocked_value_you_will_create)
    
    @pytest.mark.django_db
    @mock.patch("wallets.controllers.wallet.WalletController.list_wallets")
    def test_get_success(self, list_wallets_mock, authenticated_client):

        # You need to have mocks defined in the API call scope. You can use decorators or "with" function.
        # No function ouside of the handler scope should be really called, they should be mocked
        response = ListWalletsResponse(
            wallets = []
        )
        response.data = ["wallet1", "wallet2"]
        
        list_wallets_mock.return_value = response

        resp = authenticated_client.get(authenticated_client.url + "wallets/")
        #list_wallets_mock.assert_called_with(add args used in the call)
        assert resp.status_code == 200
        print(resp.json())

        #assert resp.json() == expected_response 1


