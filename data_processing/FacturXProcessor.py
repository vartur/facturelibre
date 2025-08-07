from datetime import datetime
from typing import Any, ClassVar

from pyfactx.CreditorFinancialAccount import CreditorFinancialAccount
from pyfactx.CreditorFinancialInstitution import CreditorFinancialInstitution
from pyfactx.DocumentLineDocument import DocumentLineDocument
from pyfactx.ExchangedDocument import ExchangedDocument
from pyfactx.ExchangedDocumentContext import ExchangedDocumentContext
from pyfactx.FacturXData import FacturXData
from pyfactx.FacturXGenerator import FacturXGenerator
from pyfactx.HeaderTradeAgreement import HeaderTradeAgreement
from pyfactx.HeaderTradeDelivery import HeaderTradeDelivery
from pyfactx.HeaderTradeSettlement import HeaderTradeSettlement
from pyfactx.InvoiceProfile import InvoiceProfile
from pyfactx.InvoiceTypeCode import InvoiceTypeCode
from pyfactx.LegalOrganization import LegalOrganization
from pyfactx.LineTradeAgreement import LineTradeAgreement
from pyfactx.LineTradeDelivery import LineTradeDelivery
from pyfactx.LineTradeSettlement import LineTradeSettlement
from pyfactx.PaymentMeansCode import PaymentMeansCode
from pyfactx.ReferencedDocument import ReferencedDocument
from pyfactx.SupplyChainTradeLineItem import SupplyChainTradeLineItem
from pyfactx.SupplyChainTradeTransaction import SupplyChainTradeTransaction
from pyfactx.TaxCategoryCode import TaxCategoryCode
from pyfactx.TaxTypeCode import TaxTypeCode
from pyfactx.TradeAddress import TradeAddress
from pyfactx.TradeParty import TradeParty
from pyfactx.TradePaymentTerms import TradePaymentTerms
from pyfactx.TradePrice import TradePrice
from pyfactx.TradeProduct import TradeProduct
from pyfactx.TradeSettlementHeaderMonetarySummation import TradeSettlementHeaderMonetarySummation
from pyfactx.TradeSettlementLineMonetarySummation import TradeSettlementLineMonetarySummation
from pyfactx.TradeSettlementPaymentMeans import TradeSettlementPaymentMeans
from pyfactx.TradeTax import TradeTax
from pyfactx.UnitCode import UnitCode
from pyfactx.UniversalCommunication import UniversalCommunication
from pyfactx.VATExemptionReasonCode import VATExemptionReasonCode


class FacturXProcessor:
    VAT_RATES: ClassVar[dict[str, TradeTax]] = {
        "0.0": TradeTax(type_code=TaxTypeCode.VALUE_ADDED_TAX, category_code=TaxCategoryCode.EXEMPT_FROM_TAX,
                        exemption_reason_code=VATExemptionReasonCode.VATEX_FR_FRANCHISE),
        "10.0": TradeTax(type_code=TaxTypeCode.VALUE_ADDED_TAX, category_code=TaxCategoryCode.STANDARD_RATE,
                         rate_applicable_percent=10.0),
        "20.0": TradeTax(type_code=TaxTypeCode.VALUE_ADDED_TAX, category_code=TaxCategoryCode.STANDARD_RATE,
                         rate_applicable_percent=20.0)

    }

    @classmethod
    def generate_facturx_xml(cls, template_data: dict[str, Any],
                             profile: InvoiceProfile = InvoiceProfile.EN16931):
        collect_vat = template_data["collect_vat"]
        client_is_pro = template_data["client_is_pro"]
        doc_context = ExchangedDocumentContext(guideline_specified_document_context_parameter=profile)
        document = ExchangedDocument(id=template_data["invoice_number"],
                                     type_code=InvoiceTypeCode.COMMERCIAL_INVOICE,
                                     issue_date_time=datetime.strptime(template_data["billing_date"], "%d %B %Y"))

        invoicer_trade_address = TradeAddress(postcode=template_data["invoicer_postcode"],
                                              line_one=template_data["invoicer_address_line_1"],
                                              city=template_data["invoicer_city"], country="FR")
        invoicer_has_trade_name = template_data["invoicer_has_trade_name"]
        invoicer_legal_org = LegalOrganization(id=template_data["invoicer_siren"].strip(),
                                               trading_business_name=template_data["invoicer_trade_name"]
                                               if invoicer_has_trade_name else None)

        vat_number = template_data.get("invoicer_vat_number", "").strip()
        vat_number = vat_number.replace(" ", "")
        specified_tax_registration = vat_number if vat_number else None

        seller = TradeParty(
            global_ids=[("0009", template_data["invoicer_siret"].strip())],
            name=template_data["invoicer_name"],
            specified_legal_organisation=invoicer_legal_org,
            trade_address=invoicer_trade_address,
            specified_tax_registration=specified_tax_registration,
            uri_universal_communication=UniversalCommunication(uri_id=template_data["invoicer_email"])
        )

        if client_is_pro:
            buyer_legal_org = LegalOrganization(id=template_data["client_siren"])
        buyer_trade_address = TradeAddress(postcode=template_data["client_postcode"],
                                           line_one=template_data["client_address_line_1"],
                                           city=template_data["client_city"],
                                           country="FR")

        client_vat_number = template_data.get("client_vat_number", "").replace(" ", "")
        buyer = TradeParty(
            name=template_data["client_name"],
            specified_legal_organisation=buyer_legal_org if client_is_pro else None,
            trade_address=buyer_trade_address,
            specified_tax_registration=client_vat_number.strip()
            if client_is_pro and collect_vat else None
        )

        line_items: list[SupplyChainTradeLineItem] = []
        line_id: int = 1
        applicable_trade_taxes: list[tuple[float, float, TradeTax]] = []

        for invoiced_item in template_data["invoiced_items"]:
            line_total_amount = round(float(invoiced_item["price"]) * int(invoiced_item["quantity"]), 2)

            if collect_vat:
                applicable_vat_rate_str = str(invoiced_item["vat_rate"])
                trade_tax = cls.VAT_RATES[applicable_vat_rate_str]
                vat_amount = float(invoiced_item["vat_amount"])
            else:
                trade_tax = TradeTax(
                    type_code=TaxTypeCode.VALUE_ADDED_TAX,
                    category_code=TaxCategoryCode.EXEMPT_FROM_TAX,
                    rate_applicable_percent=0.0
                )
                vat_amount = 0.0

            line_item = SupplyChainTradeLineItem(
                specified_trade_product=TradeProduct(name=invoiced_item["name"]),
                specified_line_trade_agreement=LineTradeAgreement(
                    net_price_product_trade_price=TradePrice(
                        charge_amount=float(invoiced_item["price"]), unit=UnitCode.ONE)),
                specified_line_trade_delivery=LineTradeDelivery(
                    billed_quantity=invoiced_item["quantity"], unit=UnitCode.ONE),
                specified_line_trade_settlement=LineTradeSettlement(
                    applicable_trade_tax=trade_tax,
                    specified_trade_settlement_line_monetary_summation=TradeSettlementLineMonetarySummation(
                        line_total_amount=line_total_amount)),
                associated_document_line_document=DocumentLineDocument(line_id=line_id)
            )

            line_id += 1
            line_items.append(line_item)
            applicable_trade_taxes.append((line_total_amount, vat_amount, trade_tax))

        monetary_summation = TradeSettlementHeaderMonetarySummation(
            tax_basis_total_amount=float(template_data["total_gross_amount"]),
            tax_total_amount=float(template_data["total_vat_amount"] if collect_vat else 0.0),
            grand_total_amount=float(template_data["total_invoice_amount"]),
            due_payable_amount=float(template_data["total_invoice_amount"]),
            line_total_amount=float(template_data["total_gross_amount"]),
            tax_currency_code=template_data["currency_code"]
        )

        payment_means: list[TradeSettlementPaymentMeans] = []
        if template_data["cash_accepted"]:
            payment_means.append(TradeSettlementPaymentMeans(
                payment_means_code=PaymentMeansCode.CASH,
                information="En espèces"))

        if template_data["cheques_accepted"]:
            payee = template_data["payee"]
            payment_means.append(TradeSettlementPaymentMeans(
                payment_means_code=PaymentMeansCode.CHEQUE,
                information=f"Par chèque à l'ordre de {payee}"))

        if template_data["bank_transfers_accepted"]:
            iban = template_data["iban"].replace(" ", "")
            bic = template_data["bic"].replace(" ", "")
            payment_means.append(TradeSettlementPaymentMeans(
                payment_means_code=PaymentMeansCode.SEPA_CREDIT_TRANSFER,
                information="Virement SEPA",
                payee_party_creditor_financial_account=CreditorFinancialAccount(
                    iban_id=iban,
                    account_name=template_data["bank_address"]),
                payee_specified_creditor_financial_institution=CreditorFinancialInstitution(
                    bic_id=bic)))

        contract_doc = ReferencedDocument(issuer_assigned_id=template_data["contract_number"])
        trade_agreement = HeaderTradeAgreement(
            seller_trade_party=seller,
            buyer_trade_party=buyer,
            contract_referenced_document=contract_doc if template_data["display_contract_number"] else None)

        payment_period_days = template_data["payment_period_days"]
        business_days = "ouvrés" if template_data["business_days"] else ""
        trade_payment_terms = TradePaymentTerms(
            due_date=datetime.strptime(template_data["payment_date"], "%d/%m/%Y"),
            description=f"Paiement à effectuer sous {payment_period_days} jours {business_days}"
        )

        trade_delivery = HeaderTradeDelivery()

        vat_breakdown: list[TradeTax] = []

        if collect_vat:
            for basis_amount, vat_amount, trade_tax in applicable_trade_taxes:
                existing_vat = next((x for x in vat_breakdown
                                     if x.rate_applicable_percent == trade_tax.rate_applicable_percent), None)
                if existing_vat:
                    existing_vat.basis_amount += basis_amount
                    existing_vat.calculated_amount += vat_amount
                else:
                    vat_breakdown.append(TradeTax(
                        type_code=trade_tax.type_code,
                        category_code=trade_tax.category_code,
                        rate_applicable_percent=trade_tax.rate_applicable_percent,
                        basis_amount=basis_amount,
                        calculated_amount=vat_amount))
        else:
            vat_breakdown.append(TradeTax(
                type_code=TaxTypeCode.VALUE_ADDED_TAX,
                category_code=TaxCategoryCode.EXEMPT_FROM_TAX,
                exemption_reason_code=VATExemptionReasonCode.VATEX_FR_FRANCHISE,
                basis_amount=template_data["total_gross_amount"],
                calculated_amount=0.0,
                rate_applicable_percent=0.0
            ))

        trade_settlement = HeaderTradeSettlement(
            invoice_currency_code=template_data["currency_code"],
            applicable_trade_tax=vat_breakdown,
            specified_trade_settlement_payment_means=payment_means,
            specified_trade_payment_terms=trade_payment_terms,
            specified_trade_settlement_header_monetary_summation=monetary_summation
        )

        transaction = SupplyChainTradeTransaction(
            included_supply_chain_trade_line_items=line_items,
            applicable_header_trade_agreement=trade_agreement,
            applicable_header_trade_delivery=trade_delivery,
            applicable_header_trade_settlement=trade_settlement
        )

        facturx_data = FacturXData(
            exchanged_document_context=doc_context,
            exchanged_document=document,
            supply_chain_transaction=transaction
        )

        return FacturXGenerator.generate(facturx_data, profile)
