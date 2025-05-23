from pydantic import BaseModel, Field, model_validator
from typing_extensions import Optional, Self


class InvoicerInfo(BaseModel):
    """
    A class representing the invoicer's company and registration details.

    Attributes:
        name (str): The invoicer's company name.
        trade_name (Optional[str]): The invoicer's trade name (if applicable).
        address_line_1 (str): The first part of the invoicer's address, including street number and name.
        postcode (str): The postcode of the invoicer's address.
        city (str): The city of the invoicer's address.
        email (str): The invoicer's email address.
        phone_number (str): The invoicer's phone number, must follow a specific pattern for French numbers.
        website (Optional[str]): The invoicer's website (if applicable).
        siren (str): The invoicer's 9-digit SIREN number.
        siret (str): The invoicer's 14-digit SIRET number.
        is_craftsman (bool): Whether the invoicer is a craftsman.
        ape_code (Optional[str]): The invoicer's APE code (if applicable).
        aprm_code (Optional[str]): The craftsman's APRM code (if applicable).
        registration_department (Optional[str]): The craftsman's registration department (if applicable).

    Methods:
        validate_invoicer_info (model_validator): Validates the consistency of the invoicer's details, ensuring:
            - The first 9 digits of the SIRET match the SIREN.
            - If the invoicer is not a craftsman, the APE code must be provided.
            - If the invoicer is a craftsman, the APRM code and registration department must be provided.

    Raises:
        ValueError: If any of the validation checks fail, such as mismatched SIREN and SIRET, or missing required details for craftsmen.
    """

    name: str = Field(..., description="The invoicer's company name")
    trade_name: Optional[str] = Field(None, description="The invoicer's trade name")
    address_line_1: str = Field(..., description="The first part of the invoicer's address (number and street name)")
    postcode: str = Field(..., description="The postcode of the invoicer's address")
    city: str = Field(..., description="The city of the invoicer's address")
    email: str = Field(..., description="The invoicer's email address")
    phone_number: str = Field(..., pattern=r'^(0[1-7])(?: \d{2}){4}$', description="The invoicer's phone number")
    website: Optional[str] = Field(None, description="The invoicer's website")
    siren: str = Field(..., pattern=r'^\d{9}$', description="The invoicer's 9-digit SIREN number")
    siret: str = Field(..., pattern=r'^\d{14}$', description="The invoicer's 14-digit SIRET number")
    is_craftsman: bool = Field(False, description="Whether or not the invoicer is a craftsman")
    ape_code: Optional[str] = Field(None, pattern=r'^\d{2}\.\d{2}[A-Z]$', description="The invoicer's APE code")
    aprm_code: Optional[str] = Field(None, description="The craftsman's APRM code")
    registration_department: Optional[str] = Field(None, pattern=r'^(0[1-9]|[1-8][0-9]|9[0-5]|2[AB]|97[1-6])$',
                                                   description="The craftsman's registration department")

    @model_validator(mode='after')
    def validate_invoicer_info(self) -> Self:
        if self.siret[:9] != self.siren:
            raise ValueError("The first 9 digits of the SIRET must match the SIREN.")
        if not self.is_craftsman and self.ape_code is None:
            raise ValueError("The APE code must be provided if the invoicer is not a craftsman")
        if self.is_craftsman and self.aprm_code is None:
            raise ValueError("The APRM code must be provided if the invoicer is a craftsman")
        if self.is_craftsman and self.registration_department is None:
            raise ValueError("The registration department must be provided if the invoicer is a craftsman")

        return self
