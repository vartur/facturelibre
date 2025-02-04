from typing import Optional

from pydantic import BaseModel, Field, model_validator
from typing_extensions import Self


class PaymentInfo(BaseModel):
    """
    A class representing the payment information for an invoice.

    Attributes:
        bank_transfers_accepted (bool): Whether bank transfers are accepted for the payment.
        iban (Optional[str]): The IBAN for bank transfer payments, if applicable.
        bic (Optional[str]): The BIC for bank transfer payments, if applicable.
        bank_address (Optional[str]): The address of the bank, if bank transfers are accepted.
        cheques_accepted (bool): Whether cheques are accepted for the payment.
        payee (Optional[str]): The payee of the cheque, if cheques are accepted.
        cash_accepted (bool): Whether cash is accepted for payment.

    Methods:
        validate_payment_info (model_validator): Validates the payment information:
            - Ensures the IBAN, BIC, and bank address are provided if bank transfers are accepted.
            - Ensures the payee is provided if cheques are accepted.

    Raises:
        ValueError: If required details (such as IBAN, BIC, or payee) are missing based on the selected payment methods.

    """

    bank_transfers_accepted: bool = Field(..., description="Whether or not bank transfers are accepted for the payment")
    iban: Optional[str] = Field(None, description="The IBAN for bank transfer payments")
    bic: Optional[str] = Field(None, description="The BIC for bank transfer payments")
    bank_address: Optional[str] = Field(None, description="The address of the bank")
    cheques_accepted: bool = Field(..., description="Whether or not cheques are accepted for the payment")
    payee: Optional[str] = Field(None, description="The payee of the cheque")
    cash_accepted: bool = Field(..., description="Whether or not cash is accepted for payment")

    @model_validator(mode='after')
    def validate_payment_info(self) -> Self:
        if self.bank_transfers_accepted:
            if self.iban is None:
                raise ValueError("The payment IBAN must be provided if bank transfers are accepted")
            if self.bic is None:
                raise ValueError("The payment BIC must be provided if bank transfers are accepted")
            if self.bank_address is None:
                raise ValueError("The bank's address must be provided if bank transfers are accepted")
        if self.cheques_accepted and self.payee is None:
            raise ValueError("The payee must be provided if cheques are accepted")
        return self
