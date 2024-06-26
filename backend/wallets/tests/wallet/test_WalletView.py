from django.http import QueryDict
from django.contrib.auth.models import User
import pytest

from unittest import mock

from wallets.schema.wallet import (
    ListWalletsRequest,
    ListWalletsResponse,
    BuildWalletRequest,
    BuildWalletResponse,
    WalletDetailsRequest,
    WalletDetailsResponse,
    UpdateWalletRequest,
    UpdateWalletResponse,
    DeleteWalletRequest,
    DeleteWalletResponse,
)
from wallets.serializers.wallet import WalletListParametersSerializer

from wallets.tests.test_fixture import api_client, test_user
from wallets.tests.wallet.test_fixture import test_wallets, test_wallets_data


class TestWalletViewAPI:

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


class TestWalletDetailViewAPI:

    @pytest.mark.django_db
    @mock.patch("wallets.controllers.wallet.WalletController.wallet_details")
    def test_get_success_owner(
        self, wallet_details_mock, api_client, test_user, test_wallets, 
    ):
        wallet_data = {
                    "id": 1,
                    "name": "John Wallet",
                    "description": "John Wallet description",
                    "owner_id": 1,
                    "co_owners": [],
                    "current_value": "0.00",
                    "created_at": "2021-10-10T12:00:00+02:00",
                    "updated_at": "2021-10-10T12:00:00+02:00",
                }

        wallet_details_mock.return_value = WalletDetailsResponse(
            data=wallet_data
        )

        api_client.force_authenticate(user=test_wallets[0].owner)
        response = api_client.get(api_client.url + f"wallets/{test_wallets[0].id}/")

        assert response.json() == wallet_data
        assert response.status_code == 200

        wallet_details_mock.assert_called_once()
        wallet_details_mock.assert_called_with(
            WalletDetailsRequest(pk=test_wallets[0].id)
        )

    @pytest.mark.django_db
    @mock.patch("wallets.controllers.wallet.WalletController.wallet_details")
    def test_get_success_co_owner(
        self, wallet_details_mock, api_client, test_wallets, 
    ):
        wallet_data = {
                    "id": 2,
                    "name": "Paul Wallet",
                    "description": "Paul Wallet description",
                    "owner_id": 2,
                    "co_owners": [test_wallets[1].co_owners.first().id],
                    "current_value": "0.00",
                    "created_at": "2021-10-10T12:00:00+02:00",
                    "updated_at": "2021-10-10T12:00:00+02:00",
                }
        
        wallet_details_mock.return_value = WalletDetailsResponse(
            data=wallet_data
        )

        api_client.force_authenticate(user=test_wallets[1].co_owners.first())
        response = api_client.get(api_client.url + f"wallets/{test_wallets[1].id}/")

        assert response.json() == wallet_data
        assert response.status_code == 200

        wallet_details_mock.assert_called_once()
        wallet_details_mock.assert_called_with(
            WalletDetailsRequest(pk=test_wallets[1].id)
        )

    @pytest.mark.django_db
    @mock.patch("wallets.controllers.wallet.WalletController.wallet_details")
    def test_get_fail_no_permission(
        self, wallet_details_mock, api_client, test_user, test_wallets
    ):

        wallet_details_mock.return_value = WalletDetailsResponse(
            data={
                    "id": 1,
                    "name": "John Wallet",
                    "description": "John Wallet description",
                    "owner_id": 1,
                    "co_owners": [],
                    "current_value": "0.00",
                    "created_at": "2021-10-10T12:00:00+02:00",
                    "updated_at": "2021-10-10T12:00:00+02:00",
                }
        )
        api_client.force_authenticate(user=test_user[0])
        response = api_client.get(api_client.url + f"wallets/{test_wallets[1].id}/")

        assert response.status_code == 403

    @pytest.mark.django_db
    @mock.patch("wallets.controllers.wallet.WalletController.wallet_details") 
    def test_get_fail_not_authorized(
        self, wallet_details_mock, api_client, test_wallets
    ):

        wallet_details_mock.return_value = WalletDetailsResponse(
            data={
                    "id": 1,
                    "name": "John Wallet",
                    "description": "John Wallet description",
                    "owner_id": 1,
                    "co_owners": [],
                    "current_value": "0.00",
                    "created_at": "2021-10-10T12:00:00+02:00",
                    "updated_at": "2021-10-10T12:00:00+02:00",
                }
        )
        response = api_client.get(api_client.url + f"wallets/{test_wallets[1].id}/")

        assert response.status_code == 401

    
    @pytest.mark.django_db
    @mock.patch("wallets.controllers.wallet.WalletController.wallet_details")
    def test_get_fail_not_found(
        self, wallet_details_mock, api_client, test_user
    ):
        wallet_details_mock.return_value = WalletDetailsResponse(
            data={}
        )

        api_client.force_authenticate(user=test_user[0])
        response = api_client.get(api_client.url + f"wallets/1000/")

        assert response.status_code == 404

    
    @pytest.mark.django_db
    @mock.patch("wallets.controllers.wallet.WalletController.update_wallet")
    def test_patch_success(
        self, wallet_update_mock, api_client, test_wallets, 
    ):
        wallet_data = {
                    "id": 1,
                    "name": "New Wallet name",
                    "description": "John Wallet description",
                    "owner_id": test_wallets[0].owner.id,
                    "co_owners": [],
                    "current_value": "0.00",
                    "created_at": "2021-10-10T12:00:00+02:00",
                    "updated_at": "2021-10-10T12:00:00+02:00",
                }

        wallet_update_mock.return_value = UpdateWalletResponse(
            data=wallet_data
        )

        api_client.force_authenticate(user=test_wallets[0].owner)
        response = api_client.patch(api_client.url + f"wallets/{test_wallets[0].id}/", {"name": "New Wallet name"})

        wallet_update_mock.assert_called_once()
        wallet_update_mock.assert_called_with(
            UpdateWalletRequest(
                pk=test_wallets[0].id,
                data={"name": "New Wallet name"},
            )
        )
        assert response.json() == wallet_data
        assert response.status_code == 201

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "request_data",
        [
            ({"name": "XX"}),
            ({"name": ""}),
            ({"name": "x" * 101}),
            ({"name": "My Wallet", "description": "x" * 1001}),
            ({"name": "My Wallet", "co_owners": [1000]}),
            ({"name": "My Wallet", "co_owners": ["xxx"]}),
            ({"name": "My Wallet", "co_owners": ["same_as_owner"]}),
        ],
    )
    @mock.patch("wallets.controllers.wallet.WalletController.update_wallet")
    def test_patch_fail(self, wallet_update_mock, api_client, test_wallets, request_data):

        api_client.force_authenticate(user=test_wallets[0].owner)
        response = api_client.patch(api_client.url + f"wallets/{test_wallets[0].id}/", request_data)

        wallet_update_mock.assert_not_called()
        assert response.status_code == 400

    @pytest.mark.django_db
    @mock.patch("wallets.controllers.wallet.WalletController.update_wallet")
    def test_patch_duplicated_name(
        self, wallet_update_mock, api_client, test_user, test_wallets
    ):

        for wallet in test_wallets:
            if wallet.owner == test_user[0]:
                request_data = {"name": wallet.name}

        api_client.force_authenticate(user=test_user[0])
        response = api_client.patch(api_client.url + f"wallets/{test_wallets[0].id}/", request_data)

        wallet_update_mock.assert_not_called()
        assert response.status_code == 400


    @pytest.mark.django_db
    @mock.patch("wallets.controllers.wallet.WalletController.update_wallet")
    def test_patch_fail_no_permission(
        self, wallet_update_mock, api_client, test_user, test_wallets
    ):

        api_client.force_authenticate(user=test_user[3])
        response = api_client.patch(api_client.url + f"wallets/{test_wallets[1].id}/", {"name": "New Wallet name"})

        wallet_update_mock.assert_not_called()
        assert response.status_code == 403

    @pytest.mark.django_db
    @mock.patch("wallets.controllers.wallet.WalletController.update_wallet")
    def test_patch_fail_not_found(
        self, wallet_update_mock, api_client, test_user
    ):

        api_client.force_authenticate(user=test_user[0])
        response = api_client.patch(api_client.url + f"wallets/1000/", {"name": "New Wallet name"})

        wallet_update_mock.assert_not_called()
        assert response.status_code == 404


    @pytest.mark.django_db
    @mock.patch("wallets.controllers.wallet.WalletController.update_wallet")
    def test_patch_fail_not_authorized(
        self, wallet_update_mock, api_client, test_wallets
    ):

        response = api_client.patch(api_client.url + f"wallets/{test_wallets[1].id}/", {"name": "New Wallet name"})

        wallet_update_mock.assert_not_called()
        assert response.status_code == 401


    @pytest.mark.django_db
    @mock.patch("wallets.controllers.wallet.WalletController.delete_wallet")
    def test_delete_success(
        self, wallet_delete_mock, api_client, test_wallets, 
    ):
        wallet_delete_mock.return_value = DeleteWalletResponse(
            pk=test_wallets[0].id
        )

        api_client.force_authenticate(user=test_wallets[0].owner)
        response = api_client.delete(api_client.url + f"wallets/{test_wallets[0].id}/")

        wallet_delete_mock.assert_called_once()
        wallet_delete_mock.assert_called_with(
            DeleteWalletRequest(pk=test_wallets[0].id)
        )

        assert response.status_code == 200
        assert response.json() == {"id": test_wallets[0].id, "message": "Wallet deleted."}


    @pytest.mark.django_db
    @mock.patch("wallets.controllers.wallet.WalletController.delete_wallet")
    def test_delete_fail_no_permission(
        self, wallet_delete_mock, api_client, test_user, test_wallets
    ):

        api_client.force_authenticate(user=test_user[3])
        response = api_client.delete(api_client.url + f"wallets/{test_wallets[1].id}/")

        wallet_delete_mock.assert_not_called()
        assert response.status_code == 403

    @pytest.mark.django_db
    @mock.patch("wallets.controllers.wallet.WalletController.delete_wallet")
    def test_delete_fail_not_found(
        self, wallet_delete_mock, api_client, test_user
    ):

        api_client.force_authenticate(user=test_user[0])
        response = api_client.delete(api_client.url + f"wallets/1000/")

        wallet_delete_mock.assert_not_called()
        assert response.status_code == 404

    @pytest.mark.django_db
    @mock.patch("wallets.controllers.wallet.WalletController.delete_wallet")
    def test_delete_fail_not_authorized(
        self, wallet_delete_mock, api_client, test_wallets
    ):

        response = api_client.delete(api_client.url + f"wallets/{test_wallets[1].id}/")

        wallet_delete_mock.assert_not_called()
        assert response.status_code == 401


    @pytest.mark.django_db
    @mock.patch("wallets.controllers.wallet.WalletController.delete_wallet")
    def test_delete_fail_no_owner(
        self, wallet_delete_mock, api_client, test_wallets
    ):

        api_client.force_authenticate(user=test_wallets[1].co_owners.first())
        response = api_client.delete(api_client.url + f"wallets/{test_wallets[1].id}/")

        wallet_delete_mock.assert_not_called()
        assert response.status_code == 403

        
