from typing import Optional

from pydantic import BaseModel, Field, model_validator
from typing_extensions import Self


class ClientInfo(BaseModel):
    """
    A class representing the basic information about a client.

    Attributes:
        name (str): The client's name.
        address_line_1 (str): The first part of the client's address, including the street number and name.
        postcode (str): The postcode of the client's address.
        city (str): The city of the client's address.
        is_pro (bool): Indicates whether the client is a professional (business entity).
        siren (Optional[str]): The client's 9-digit SIREN number. If the client is a professional, this must be provided.

    Methods:
        validate_client_info (model_validator): Validates that the SIREN number is provided if the client is marked as a professional.

    Raises:
        ValueError: If the client is marked as a professional but the SIREN number is not provided.

    """

    name: str = Field(..., description="The client's name")
    address_line_1: str = Field(..., description="The first part of the client's address (number and street name)")
    postcode: str = Field(..., description="The postcode of the client's address")
    city: str = Field(..., description="The city of the client's address")
    is_pro: bool = Field(False, description="Whether or not the client is a professional")
    siren: Optional[str] = Field(None, pattern=r'^\d{9}$', description="The client's 9-digit SIREN number")

    @model_validator(mode='after')
    def validate_client_info(self) -> Self:
        if self.is_pro and self.siren is None:
            raise ValueError("The SIREN must be provided if the client is a professional")
        return self
