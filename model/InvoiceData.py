from typing import Optional

from pydantic import BaseModel, Field, model_validator
from typing_extensions import Self

from model.BillingDetails import BillingDetails
from model.ClientInfo import ClientInfo
from model.InvoicedItem import InvoicedItem
from model.InvoicerInfo import InvoicerInfo
from model.PaymentInfo import PaymentInfo
from model.RcProInfo import RcProInfo


class InvoiceData(BaseModel):
    """
    A class representing the detailed data of an invoice.

    Attributes:
        invoice_number (str): The unique invoice number.
        collect_vat (bool): Whether the VAT is collected on this invoice.
        invoicer_info (InvoicerInfo): Information about the invoicer (business entity).
        logo_uri (Optional[str]): The URI of the invoicer's logo.
        client_info (ClientInfo): Information about the client being invoiced.
        payment_info (PaymentInfo): The payment information associated with the invoice.
        rc_pro_info (Optional[RcProInfo]): The RC PRO information, if applicable.
        invoiced_items (list[InvoicedItem]): The list of items that are being invoiced.
        billing_details (BillingDetails): Information about the billing details for the invoice.
        contract_number (Optional[str]): The contract number associated with this invoice.

    Methods:
        validate_invoice_data (model_validator): Validates that each invoiced item has a VAT rate if VAT is being collected.

    Raises:
        ValueError: If the VAT is collected but any invoiced item lacks a VAT rate.

    """

    invoice_number: str = Field(..., description="The invoice number")
    collect_vat: bool = Field(False, description="Whether or not the VAT is collected on this invoice")
    invoicer_info: InvoicerInfo = Field(..., description="The invoicer's information")
    logo_uri: Optional[str] = Field(None, description="The URI of the invoicer's logo")
    client_info: ClientInfo = Field(..., description="The client's information")
    payment_info: PaymentInfo = Field(..., description="The invoice's payment information")
    rc_pro_info: Optional[RcProInfo] = Field(None, description="The RC PRO information")
    invoiced_items: list[InvoicedItem] = Field(..., description="The invoiced items")
    billing_details: BillingDetails = Field(..., description="The invoice's billing details")
    contract_number: Optional[str] = Field(None, description="The contract number related to this invoice")

    @model_validator(mode='after')
    def validate_invoice_data(self) -> Self:
        if self.collect_vat:
            for item in self.invoiced_items:
                if item.vat_rate is None:
                    raise ValueError("The invoiced item VAT rate must be provided if the VAT is collected")
        return self
