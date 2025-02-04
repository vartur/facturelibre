from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator
from typing_extensions import Self

from model.PaymentPeriodDetails import PaymentPeriodDetails


class BillingDetails(BaseModel):
    """
    A class representing the details of a billing period.

    Attributes:
        bill_whole_current_month (bool): Indicates whether the billing period is the whole current month.
        billing_period_start (Optional[str]): The start date of the billing period, formatted as DD/MM/YYYY.
        billing_period_end (Optional[str]): The end date of the billing period, formatted as DD/MM/YYYY.
        billing_date_is_today (bool): Indicates whether the billing date is today.
        billing_date_is_end_of_current_month (bool): Indicates whether the billing date is the end of the current month.
        billing_date (Optional[str]): The billing date, formatted as DD/MM/YYYY.
        payment_period_details (PaymentPeriodDetails): A detailed object containing information about the payment period.

    Methods:
        validate_start_date (field_validator): Validates that the billing period start date is in DD/MM/YYYY format.
        validate_end_date (field_validator): Validates that the billing period end date is in DD/MM/YYYY format.
        validate_billing_date (field_validator): Validates that the billing date is in DD/MM/YYYY format.
        validate_billing_details (model_validator): Performs additional checks on the consistency of the billing details.

    Raises:
        ValueError: If any of the dates are in an incorrect format or if the billing details are inconsistent.

    """

    bill_whole_current_month: bool = Field(False,
                                           description="Whether or not the billing period is the whole current month")
    billing_period_start: Optional[str] = Field(None, description="The start date of the billing period")
    billing_period_end: Optional[str] = Field(None, description="The end date of the billing period")
    billing_date_is_today: bool = Field(False, description="Whether or not the billing date is today")
    billing_date_is_end_of_current_month: bool = Field(False,
                                                       description="Whether or not the billing date is the end of the current month")
    billing_date: Optional[str] = Field(None, description="The billing date")
    payment_period_details: PaymentPeriodDetails = Field(..., description="The payment period details")

    @field_validator("billing_period_start")
    def validate_start_date(cls, billing_period_start):
        try:
            datetime.strptime(billing_period_start, "%d/%m/%Y")
        except ValueError:
            raise ValueError("The billing period start date must be in the format DD/MM/YYYY")
        return billing_period_start

    @field_validator("billing_period_end")
    def validate_end_date(cls, billing_period_end):
        try:
            datetime.strptime(billing_period_end, "%d/%m/%Y")
        except ValueError:
            raise ValueError("The billing period end date must be in the format DD/MM/YYYY")
        return billing_period_end

    @field_validator("billing_date")
    def validate_billing_date(cls, billing_date):
        try:
            datetime.strptime(billing_date, "%d/%m/%Y")
        except ValueError:
            raise ValueError("The billing date must be in the format DD/MM/YYYY")
        return billing_date

    @model_validator(mode='after')
    def validate_billing_details(self) -> Self:
        if not self.bill_whole_current_month:
            if self.billing_period_start is None:
                raise ValueError("The start date of the billing period must be provided")
            if self.billing_period_end is None:
                raise ValueError("The end date of the billing period must be provided")

        if self.billing_date_is_today and self.billing_date_is_end_of_current_month:
            raise ValueError("The billing date cannot be simultaneously today and at the end of the current month")

        if not self.billing_date_is_today and not self.billing_date_is_end_of_current_month:
            if self.billing_date is None:
                raise ValueError("The billing date must be provided")

        return self
