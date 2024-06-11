from django.conf import settings
from django.contrib.auth.models import User

from rest_framework.request import Request

from wallets.serializers import WalletSerializer


class ListWalletsRequest:
    """
    Request object for listing wallets controller.

    This class is used to encapsulate the data from a request in a structured way.

    Attributes:
        parameters (dict): A dictionary with the query parameters of the request.
        user (User): The user making the request.

    """

    def __init__(self, request: Request) -> None:
        self.parameters = request.query_params.dict()
        self.user = request.user


class ListWalletsResponse:
    """
    Response object for listing wallets controller.

    This class is used to encapsulate the response data for a wallet controller in a structured way.
    It is initialized with a list of Wallet objects from which it extracts the data and constructs the response.

    Attributes:
        wallets (List[Wallet]): A list of wallet instances.
        data (dict): The serialized data of the wallets.
        status (int): The HTTP status code of the response.

    """

    serializer = WalletSerializer

    def __init__(self, wallets) -> None:

        self.wallets = wallets
        self.status = 200
        self.data = self.serializer(wallets, many=True).data


class BuildWalletRequest:
    """
    Request object for building a wallet controller.

    This class is used to encapsulate the data from a request in a structured way.

    Attributes:
        data (dict): The data of the request.
        owner (User): The user making the request.
    """

    def __init__(self, request: Request) -> None:
        self.data = request.data
        self.owner = request.user


class BuildWalletResponse:
    """
    Response object for building a wallet controller.

    This class is used to encapsulate the response data for a wallet controller in a structured way.
    It is initialized with a Wallet object from which it extracts the data and constructs the response.

    Attributes:
        wallet (Wallet): The wallet instance that the response is about.
        data (dict): The serialized data of the wallet. Only specific fields are included in this data.
        status (int): The HTTP status code of the response.
        location (str): The URL location of the wallet.
    """

    serializer = WalletSerializer

    def __init__(self, wallet) -> None:
        self.wallet = wallet

        all_data = self.serializer(wallet).data
        fields = ["id", "name", "owner_id", "co_owners", "description"]

        self.data = {field: all_data[field] for field in fields}
        self.status = 201
        self.location = f"{settings.API_ROOT_PATH}wallets/{wallet.id}"


class WalletDetailsRequest:
    """
    Request object for getting wallet details controller.

    This class is used to encapsulate the data from a request in a structured way.

    Attributes:
        pk (int): The primary key of the wallet.
    """

    def __init__(self, pk: int) -> None:
        self.pk = pk


class WalletDetailsResponse:
    """
    Response object for getting wallet details controller.

    This class is used to encapsulate the response data for a wallet controller in a structured way.
    It is initialized with a Wallet object from which it extracts the data and constructs the response.

    Attributes:
        wallet (Wallet): The wallet instance that the response is about.
        data (dict): The serialized data of the wallet.
        status (int): The HTTP status code of the response.
    """

    serializer = WalletSerializer

    def __init__(self, wallet) -> None:
        self.wallet = wallet
        self.status = 200

        if wallet is not None:
            self.data = self.serializer(wallet).data
        else:
            self.data = None


class DeleteWalletRequest:
    """
    Request object for deleting a wallet controller.

    This class is used to encapsulate the data from a request in a structured way.

    Attributes:
        pk (int): The primary key of the wallet.
    """

    def __init__(self, pk: int) -> None:
        self.pk = pk


class DeleteWalletResponse:
    """
    Response object for deleting a wallet controller.

    This class is used to encapsulate the response data for a wallet controller in a structured way.

    Attributes:
        status (int): The HTTP status code of the response.
    """

    def __init__(self, status: int) -> None:
        self.status = 200


class UpdateWalletRequest:
    """
    Request object for updating a wallet controller.

    This class is used to encapsulate the data from a request in a structured way.

    Attributes:
        pk (int): The primary key of the wallet.
        data (dict): The data of the request.
    """

    def __init__(self, pk: int, data: dict) -> None:
        self.pk = pk
        self.data = data


class UpdateWalletResponse:
    """
    Response object for updating a wallet controller.

    This class is used to encapsulate the response data for a wallet controller in a structured way.
    It is initialized with a Wallet object from which it extracts the data and constructs the response.

    Attributes:
        wallet (Wallet): The wallet instance that the response is about.
        data (dict): The serialized data of the wallet. Only specific fields are included in this data.
        status (int): The HTTP status code of the response.
    """

    def __init__(self, wallet) -> None:
        self.wallet = wallet

        all_data = self.serializer(wallet).data
        fields = ["id", "name", "owner_id", "co_owners", "description"]

        self.data = {field: all_data[field] for field in fields}
        self.status = 200
