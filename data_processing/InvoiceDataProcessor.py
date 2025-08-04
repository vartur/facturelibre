import locale
import re
from datetime import datetime, timedelta
from typing import Any

import numpy
from holidays.countries import France

from currency_symbols import CurrencySymbols

from model.InvoiceData import InvoiceData


def format_price(price: float) -> str:
    """
   Format a price value into a string with two decimal places and grouping for thousands.

   Args:
       price (float): The price to format.

   Returns:
       str: The formatted price as a string.
   """
    return locale.format_string("%.2f", price, grouping=True).replace('.', ',')


def format_vat_rate(vat_rate: float) -> str:
    """
    Format a VAT rate value into a string with one decimal place.

    Args:
        vat_rate (float): The VAT rate to format.

    Returns:
        str: The formatted VAT rate as a string.
    """
    return locale.format_string("%.1f", vat_rate).replace('.', ',')


def format_siren(siren: str) -> str:
    """
    Format a SIREN number by grouping it into blocks of three digits.

    Args:
        siren (str): The SIREN number to format.

    Returns:
        str: The formatted SIREN number.
    """
    return " ".join(siren[i:i + 3] for i in range(0, len(siren), 3))


def format_siret(siret: str) -> str:
    """
   Format a SIRET number by grouping it into blocks.

   Args:
       siret (str): The SIRET number to format.

   Returns:
       str: The formatted SIRET number.
   """
    return f"{siret[:3]} {siret[3:6]} {siret[6:9]} {siret[9:]}"


def format_vat_number(vat_number: str) -> str:
    """
    Format a VAT number by adding spaces in appropriate positions.

    Args:
        vat_number (str): The VAT number to format.

    Returns:
        str: The formatted VAT number.
    """
    return f"{vat_number[:2]} {vat_number[2:4]} {vat_number[4:]}"


def format_iban(iban: str) -> str:
    """
    Format an IBAN number by grouping it into blocks of four characters.

    Args:
        iban (str): The IBAN number to format.

    Returns:
        str: The formatted IBAN number.
    """
    iban = ''.join(iban.split())
    return ' '.join([iban[i:i + 4] for i in range(0, len(iban), 4)])


def format_bic(bic: str) -> str:
    """
   Format a BIC number by grouping it into blocks of four characters.

   Args:
       bic (str): The BIC number to format.

   Returns:
       str: The formatted BIC number.
   """
    bic = ''.join(bic.split())
    if len(bic) == 8:
        bic += 'XXX'
    return ' '.join([bic[i:i + 4] for i in range(0, len(bic), 4)])


def calculate_vat_number_from_siren(siren: str) -> str:
    """
   Calculate a French VAT number based on a given SIREN number.

   Args:
       siren (str): The SIREN number to generate the VAT number from.

   Raises:
       ValueError: If the SIREN number is not a valid 9-digit number.

   Returns:
       str: The generated VAT number in the format "FR XX SIREN".
   """

    # Ensure the SIREN is a 9-digit number
    siren = str(siren).zfill(9)  # Ensure it's 9 digits, padding with zeros if needed
    if len(siren) != 9 or not siren.isdigit():
        raise ValueError("Invalid SIREN number. Must be 9 digits.")

    # Calculate the checksum using the SIREN number
    siren_number = int(siren)
    checksum = (12 + 3 * (siren_number % 97)) % 97

    # Format checksum to two digits (e.g., "03" instead of "3")
    checksum_str = f"{checksum:02}"

    # Create the VAT number
    vat_number = f"FR {checksum_str} {siren}"
    return vat_number


class InvoiceDataProcessor:
    """
    A class to process invoice data and generate formatted information for invoicing.

    Attributes:
        invoice_data (InvoiceData): The invoice data to process.
    """

    def __init__(self, invoice_data: InvoiceData):
        """
        Initializes the InvoiceDataProcessor with the given invoice data.

        Args:
            invoice_data (InvoiceData): The invoice data to process.
        """
        self.invoice_data = invoice_data

    def get_billing_date_string(self, date_format: str = '%d %B %Y'):
        """
       Get the formatted billing date string based on the billing details.

       Args:
           date_format (str): The format to use for the billing date (default: '%d %B %Y').

       Returns:
           str: The formatted billing date.
       """
        billing_details = self.invoice_data.billing_details
        if billing_details.billing_date_is_today:
            return datetime.today().strftime(date_format)
        elif billing_details.billing_date_is_end_of_current_month:
            return ((datetime.now().replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)).strftime(
                date_format)
        else:
            return datetime.strptime(billing_details.billing_date, '%d/%m/%Y').strftime(date_format)

    def get_invoice_payment_date(self):
        """
        Get the invoice payment date based on the payment period details.

        Returns:
            str: The formatted payment date.
        """
        billing_details = self.invoice_data.billing_details
        payment_period_details = billing_details.payment_period_details

        billing_date = datetime.strptime(self.get_billing_date_string("%d/%m/%Y"), "%d/%m/%Y")
        if payment_period_details.payment_date is not None:
            return payment_period_details.payment_date
        elif payment_period_details.business_days_only:
            french_bank_holidays = []
            for date, name in sorted(France(years=[datetime.today().year, datetime.today().year + 1]).items()):
                french_bank_holidays.append(numpy.datetime64(date))
            payment_date = \
                numpy.busday_offset([numpy.datetime64(billing_date.strftime("%Y-%m-%d"))],
                                    payment_period_details.number_of_days,
                                    roll='backward',
                                    holidays=french_bank_holidays)[0].astype(datetime)
            return payment_date.strftime("%d/%m/%Y")
        else:
            payment_date = billing_date + timedelta(days=payment_period_details.number_of_days)
            return payment_date.strftime("%d/%m/%Y")

    def get_billing_period_start(self):
        """
        Get the start of the billing period.

        Returns:
            str: The formatted start date of the billing period.
        """
        billing_details = self.invoice_data.billing_details
        if billing_details.bill_whole_current_month:
            return f'{datetime.now().replace(day=1):%d/%m/%Y}'
        else:
            return billing_details.billing_period_start

    def get_billing_period_end(self):
        """
        Get the end of the billing period.

        Returns:
            str: The formatted end date of the billing period.
        """
        billing_details = self.invoice_data.billing_details
        if billing_details.bill_whole_current_month:
            return f'{(datetime.now().replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1):%d/%m/%Y}'
        else:
            return billing_details.billing_period_end

    def get_items_details(self, formatted: bool = False):
        """
        Get the details of the invoiced items, including price, quantity, and total amount.

        Args:
            formatted (bool): Whether to format the amounts or return them as raw floats (default: False).

        Returns:
            list[dict]: A list of dictionaries containing invoiced item details.
        """
        item_details = list()
        for item in self.invoice_data.invoiced_items:
            gross_amount = item.price * item.quantity
            if self.invoice_data.collect_vat:
                vat_amount = round((item.vat_rate / 100) * item.price * item.quantity, 2)
                total_amount = gross_amount + vat_amount
                item_details.append(
                    {"name": item.name, "price": format_price(item.price) if formatted else f'{item.price:.2f}',
                     "quantity": item.quantity,
                     "gross_amount": format_price(gross_amount) if formatted else f'{gross_amount:.2f}',
                     "vat_rate": format_vat_rate(item.vat_rate) if formatted else f'{item.vat_rate:.1f}',
                     "total_amount": format_price(total_amount) if formatted else f'{total_amount:.2f}',
                     "vat_amount": f'{vat_amount:.2f}'})
            else:
                item_details.append(
                    {"name": item.name, "price": format_price(item.price) if formatted else f'{item.price:.2f}',
                     "quantity": item.quantity,
                     "gross_amount": format_price(gross_amount) if formatted else f'{gross_amount:.2f}'})
        return item_details

    def get_invoice_gross_amount(self) -> float:
        """
        Get the total gross amount of the invoice.

        Returns:
            float: The total gross amount of the invoice.
        """
        gross_amount = 0.0
        for item_details in self.get_items_details():
            gross_amount += float(item_details["gross_amount"])
        return gross_amount

    def get_invoice_vat_amount(self) -> float:
        """
        Get the total VAT amount of the invoice.

        Returns:
            float: The total VAT amount of the invoice.
        """
        vat_amount = 0.0
        if self.invoice_data.collect_vat:
            for item_details in self.get_items_details():
                vat_amount += float(item_details["vat_amount"])
        return vat_amount

    def get_invoice_total(self) -> float:
        """
        Get the total amount (gross amount + VAT) of the invoice.

        Returns:
            float: The total amount of the invoice.
        """
        return self.get_invoice_gross_amount() + self.get_invoice_vat_amount()

    def get_phone_number_with_country_code(self, country_code: str = '+33') -> str:
        """
        Format the invoicer's phone number with a given country code.

        Args:
            country_code (str): The country code to prepend (default: '+33').

        Returns:
            str: The formatted phone number.
        """
        # Remove all non-digit characters from the phone number
        digits_only = ''.join([char for char in self.invoice_data.invoicer_info.phone_number if char.isdigit()])

        # Remove leading zero, if present
        if digits_only.startswith('0'):
            digits_only = digits_only[1:]

        # Prepend the country code
        formatted_number = f"{country_code}{digits_only}"

        return formatted_number

    def create_html_link_keep_www(self, url):
        """Version that keeps www in the display text if present in input"""
        if not url.startswith(('http://', 'https://')):
            if url.startswith('www.'):
                url = 'https://' + url
            else:
                url = 'https://www.' + url

        display_text = re.sub(r'^https?://', '', url)
        return f'<a href="{url}" target="_blank">{display_text}</a>'

    def get_template_data(self, formatted: bool = True) -> dict[str, Any]:
        """
        Generate a dictionary containing invoice data formatted for use in a template.

        Args:
            formatted (bool): Whether to format monetary values for display (default: True).

        Returns:
            dict[str, Any]: A dictionary containing invoice-related information, including:
                - Invoicer details (name, address, SIREN, SIRET, VAT number, etc.).
                - Client details (name, address, SIREN, VAT number, etc.).
                - Invoice details (number, billing date, period, contract number, etc.).
                - Invoiced items, including pricing details.
                - Payment details (accepted methods, IBAN, BIC, payment terms).
                - Professional liability insurance details (if applicable).
        """
        invoicer_info = self.invoice_data.invoicer_info
        client_info = self.invoice_data.client_info
        payment_period_details = self.invoice_data.billing_details.payment_period_details
        payment_info = self.invoice_data.payment_info
        rc_pro_info = self.invoice_data.rc_pro_info
        html_data = {"invoice_number": self.invoice_data.invoice_number,
                     "collect_vat": self.invoice_data.collect_vat,
                     "display_logo": self.invoice_data.logo_uri is not None,
                     "logo_uri": self.invoice_data.logo_uri,
                     "invoicer_name": invoicer_info.name,
                     "invoicer_has_trade_name": invoicer_info.trade_name is not None,
                     "invoicer_trade_name": invoicer_info.trade_name,
                     "invoicer_address_line_1": invoicer_info.address_line_1,
                     "invoicer_postcode": invoicer_info.postcode,
                     "invoicer_city": invoicer_info.city,
                     "invoicer_siren": format_siren(invoicer_info.siren),
                     "invoicer_siret": format_siret(invoicer_info.siret),
                     "invoicer_is_craftsman": invoicer_info.is_craftsman,
                     "aprm_code": invoicer_info.aprm_code,
                     "registration_dep": invoicer_info.registration_department,
                     "ape_code": invoicer_info.ape_code,
                     "invoicer_vat_number": calculate_vat_number_from_siren(
                         invoicer_info.siren),
                     "invoicer_email": invoicer_info.email,
                     "invoicer_phone_number": invoicer_info.phone_number,
                     "full_phone_number": self.get_phone_number_with_country_code(),
                     "invoicer_has_website": invoicer_info.website is not None,
                     "invoicer_website": self.create_html_link_keep_www(
                         invoicer_info.website) if invoicer_info.website is not None else "",
                     "client_name": client_info.name,
                     "client_address_line_1": client_info.address_line_1,
                     "client_postcode": client_info.postcode,
                     "client_city": client_info.city,
                     "client_is_pro": client_info.is_pro,
                     "client_siren": format_siren(client_info.siren) if client_info.is_pro else "",
                     "client_vat_number": calculate_vat_number_from_siren(
                         client_info.siren) if client_info.is_pro and self.invoice_data.collect_vat else "",
                     "display_contract_number": self.invoice_data.contract_number is not None,
                     "contract_number": self.invoice_data.contract_number,
                     "billing_date": self.get_billing_date_string().upper(),
                     "billing_period_start": self.get_billing_period_start(),
                     "billing_period_end": self.get_billing_period_end(),
                     "invoiced_items": self.get_items_details(formatted=formatted),
                     "total_gross_amount": format_price(
                         self.get_invoice_gross_amount()) if formatted else f'{self.get_invoice_gross_amount():.2f}',
                     "total_vat_amount": (format_price(
                         self.get_invoice_vat_amount()) if formatted else f'{self.get_invoice_vat_amount():.2f}') if self.invoice_data.collect_vat else "",
                     "total_invoice_amount": format_price(
                         self.get_invoice_total()) if formatted else f'{self.get_invoice_total():.2f}',
                     "payment_period_days": payment_period_details.number_of_days,
                     "business_days": payment_period_details.business_days_only,
                     "payment_date": self.get_invoice_payment_date(),
                     "currency_code": payment_info.currency_code,
                     "currency_symbol": CurrencySymbols.get_symbol(payment_info.currency_code),
                     "bank_transfers_accepted": payment_info.bank_transfers_accepted,
                     "iban": format_iban(payment_info.iban) if payment_info.iban else "",
                     "bic": format_bic(payment_info.bic) if payment_info.bic else "",
                     "bank_address": payment_info.bank_address,
                     "cheques_accepted": payment_info.cheques_accepted,
                     "payee": payment_info.payee,
                     "cash_accepted": payment_info.cash_accepted,
                     "display_rc_pro": rc_pro_info is not None,
                     "rc_pro_name": rc_pro_info.name if rc_pro_info is not None else "",
                     "rc_pro_address_line_1": rc_pro_info.address_line_1 if rc_pro_info is not None else "",
                     "rc_pro_address_line_2": rc_pro_info.address_line_2 if rc_pro_info is not None else "",
                     "rc_pro_geo_cov": rc_pro_info.geographical_coverage if rc_pro_info is not None else "",
                     }

        return html_data
