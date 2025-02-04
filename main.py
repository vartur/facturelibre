import locale
import logging
import sys

from jinja2 import Environment, FileSystemLoader
from pydantic import ValidationError
from weasyprint import HTML

from data_processing.InvoiceDataProcessor import InvoiceDataProcessor
from model.InvoiceData import InvoiceData

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logging.getLogger("weasyprint").setLevel(logging.ERROR)
logging.getLogger("fontTools").setLevel(logging.ERROR)
logging.getLogger("fontTools.ttLib").setLevel(logging.ERROR)
logging.getLogger("fontTools.subset").setLevel(logging.ERROR)


def generate_pdf_invoice(invoice_data_json: str, invoice_locale='fr_FR.UTF-8') -> str:
    # Set the locale (French UTF-8 by default)
    locale.setlocale(locale.LC_ALL, invoice_locale)

    # Load the invoice data and validate it against the Pydantic model
    logging.info("Loading the invoice data...")
    try:
        invoice_data = InvoiceData.model_validate_json(invoice_data_json)
    except ValidationError as ve:
        inv_pars = [
            (f"/{'/'.join(map(str, e['loc']))}",
             f"{e['type']}, {e['msg']}")
            for e in ve.errors()
        ]
        logging.error(f"Errors occurred during the validation of the invoice data: {inv_pars}")
        return "Validation failed"

    # Pre-process the data to get the template arguments
    logging.info("Pre-processing the invoice data...")
    template_data = InvoiceDataProcessor(invoice_data).get_template_data()

    # Read the CSS and add it to the template data
    with open('static/css/style.css', 'r') as f:
        inline_css = f.read()
    template_data["inline_css"] = inline_css

    # Apply the data to the HTML template
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('html/invoice.html')
    html_content = template.render(template_data)

    # Set the PDF metadata
    title = f"FACTURE N°{invoice_data.invoice_number} - {invoice_data.client_info.name}"

    # Generate the PDF from HTML
    logging.info("Generating the PDF invoice...")
    pdf_file_name = f"{title}.pdf"
    pdf_document = HTML(string=html_content).render()

    pdf_document.write_pdf(pdf_file_name, pdf_variant='pdf/a-3b')

    return title


def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <invoice_data_file>")
        sys.exit(1)

    filename = sys.argv[1]

    try:
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()
            pdf_invoice = generate_pdf_invoice(content)
            logging.info(f"Successfully generated PDF invoice '{pdf_invoice}.pdf'")
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
