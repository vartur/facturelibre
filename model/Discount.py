from enum import StrEnum
from typing import Optional, Self

from pydantic import BaseModel, Field, model_validator


class DiscountType(StrEnum):
    PERCENTAGE = "Percentage"
    AMOUNT = "Amount"


class Discount(BaseModel):
    discount_type: DiscountType = Field(...)
    percentage: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    amount: Optional[float] = Field(default=None, gt=0.0)

    @model_validator(mode='after')
    def validate_discount(self) -> Self:
        if self.discount_type == DiscountType.PERCENTAGE:
            if self.percentage is None:
                raise ValueError("The percentage must be provided if the discount type is percentage")
        elif self.discount_type == DiscountType.AMOUNT:
            if self.amount is None:
                raise ValueError("The amount must be provided if the discount type is amount")
        return self
