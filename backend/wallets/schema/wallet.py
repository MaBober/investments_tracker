from pydantic import BaseModel
from typing import Any, Dict, List


class ListWalletsRequest(BaseModel):
    """
    Represents a request to list wallets.

    Attributes:
        query_parameters (Dict[str, Any]): The query parameters for the request.
        user_id (int): The primary key of the user making the request.
        user_is_staff (bool): A flag indicating if the user is a staff member or not.

    """

    query_parameters: Dict[str, Any]
    user_id: int
    user_is_staff: bool


class ListWalletsResponse(BaseModel):
    """
    Response object for listing wallets controller.

    This class is used to encapsulate the response data for a wallet controller in a structured way.
    It is initialized with a list of Wallet objects from which it extracts the data and constructs the response.

    Attributes:
        data (List[Dict[str, Any]]): The serialized data of the wallets.
        status (int): The HTTP status code of the response.

    """

    data: List[Dict[str, Any]]
    status: int = 200


class BuildWalletRequest(BaseModel):
    """
    Request object for building a wallet controller.

    This class is used to encapsulate the data from a request in a structured way.

    Attributes:
        data (Dict[str, Any]): The data of the request.
        owner_id (int): The primary key of the owner of the wallet.
    """

    data: Dict[str, Any]
    owner_id: int


class BuildWalletResponse(BaseModel):
    """
    Response object for building a wallet controller.

    This class is used to encapsulate the response data for a wallet controller in a structured way.
    It is initialized with a Wallet object from which it extracts the data and constructs the response.

    Attributes:
        data (Dict[str, Any]): The serialized data of the wallet.
        status (int): The HTTP status code of the response.
        location (str): The URL location of the wallet.
    """

    data: Dict[str, Any]
    status: int = 201
    location: str


class WalletDetailsRequest(BaseModel):
    """
    Request object for getting wallet details controller.

    This class is used to encapsulate the data from a request in a structured way.

    Attributes:
        pk (int): The primary key of the wallet.
    """

    pk: int


class WalletDetailsResponse(BaseModel):
    """
    Response object for getting wallet details controller.

    This class is used to encapsulate the response data for a wallet controller in a structured way.
    It is initialized with a Wallet object from which it extracts the data and constructs the response.

    Attributes:

        data (Dict[str, Any]): The serialized data of the wallet.
        status (int): The HTTP status code of the response.
    """

    data: Dict[str, Any]
    status: int = 200


class DeleteWalletRequest(BaseModel):
    """
    Request object for deleting a wallet controller.

    This class is used to encapsulate the data from a request in a structured way.

    Attributes:
        pk (int): The primary key of the wallet.
    """

    pk: int


class DeleteWalletResponse(BaseModel):
    """
    Response object for deleting a wallet controller.

    This class is used to encapsulate the response data for a wallet controller in a structured way.

    Attributes:
        status (int): The HTTP status code of the response.
    """

    status: int = 200


class UpdateWalletRequest(BaseModel):
    """
    Request object for updating a wallet controller.

    This class is used to encapsulate the data from a request in a structured way.

    Attributes:
        pk (int): The primary key of the wallet.
        data (Dict[str, Any]): The data of the request.
    """

    pk: int
    data: Dict[str, Any]


class UpdateWalletResponse(BaseModel):
    """
    Response object for updating a wallet controller.

    This class is used to encapsulate the response data for a wallet controller in a structured way.

    Attributes:
        data (Dict[str, Any]): The serialized data of the wallet.
        status (int): The HTTP status code of the response.
    """

    data: Dict[str, Any]
    status: int = 201
