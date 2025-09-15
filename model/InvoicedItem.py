from typing import Optional

from pydantic import BaseModel, Field, model_validator
from typing_extensions import Self

from model.Discount import Discount


class InvoicedItem(BaseModel):
    """
    A class representing an individual item on the invoice.

    Attributes:
        name (str): The name or description of the invoiced item.
        price (float): The price of the invoiced item. Must be greater than 0.
        quantity (float): The quantity of the invoiced item. Must be greater than 0.
        vat_rate (Optional[float]): The VAT rate applied to the invoiced item, between 0 and 100. Optional.

    Methods:
        validate_invoice_item (model_validator): Validates that the price has at most two decimal places and
                                                  the VAT rate, if provided, has at most one decimal place.

    Raises:
        ValueError: If the price has more than two decimal places, or the VAT rate has more than one decimal place.

    """

    name: str = Field(..., description="The invoiced item's name")
    price: float = Field(..., gt=0.00, description="The invoiced item's price")
    quantity: float = Field(..., gt=0.00, description="The quantity of invoice items")
    vat_rate: Optional[float] = Field(None, gt=0.0, le=100.0, description="The invoiced item's VAT rate")
    discount: Optional[Discount] = Field(None, description="The discount applied to the invoiced item")

    @model_validator(mode='after')
    def validate_invoice_item(self) -> Self:
        if round(self.price, 2) != self.price:
            raise ValueError("The price must have at most two decimal places")
        if self.vat_rate is not None and round(self.vat_rate, 1) != self.vat_rate:
            raise ValueError("The VAT rate must have at most one decimal place")
        return self
