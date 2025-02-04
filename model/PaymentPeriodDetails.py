from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class PaymentPeriodDetails(BaseModel):
    """
    A class representing the payment period details for an invoice.

    Attributes:
        number_of_days (int): The number of days allowed for paying the invoice (default is 30).
        business_days_only (bool): Whether the payment period should be calculated using business days only (default is False).
        payment_date (Optional[str]): The payment date, formatted as DD/MM/YYYY, if provided.

    Methods:
        validate_payment_date (field_validator): Validates that the payment date is in the correct DD/MM/YYYY format.

    Raises:
        ValueError: If the payment date is provided but is not in the DD/MM/YYYY format.

    """

    number_of_days: int = Field(30, description="The number of days to pay the invoice")
    business_days_only: bool = Field(False,
                                     description="Whether the payment period should be computed in business days only")
    payment_date: Optional[str] = Field(None, description="The payment date")

    @field_validator('payment_date')
    def validate_payment_date(cls, payment_date):
        try:
            datetime.strptime(payment_date, "%d/%m/%Y")
        except ValueError:
            raise ValueError("The payment date must be in the format DD/MM/YYYY")
        return payment_date
