import locale
import logging
import sys
from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from lxml import etree as ET
from pydantic import ValidationError

from weasyprint import HTML, Attachment

from data_processing.FacturXProcessor import FacturXProcessor
from data_processing.InvoiceDataProcessor import InvoiceDataProcessor
from model.InvoiceData import InvoiceData


def setup_logging():
    """Configure logging with proper formatting and levels."""
    # Remove existing handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Suppress verbose logging from third-party libraries
    for logger_name in ["weasyprint", "fontTools", "fontTools.ttLib", "fontTools.subset"]:
        logging.getLogger(logger_name).setLevel(logging.ERROR)


def validate_file_paths():
    """Validate that required files and directories exist."""
    required_files = [
        Path('static/css/style.css'),
        Path('templates/html/invoice.html')
    ]

    missing_files = [file for file in required_files if not file.exists()]
    if missing_files:
        raise FileNotFoundError(f"Required files not found: {missing_files}")


def generate_pdf_invoice(invoice_data_json: str, invoice_locale: str = 'fr_FR.UTF-8') -> Optional[str]:
    """
    Generate a PDF invoice from JSON data.
    
    Args:
        invoice_data_json: JSON string containing invoice data
        invoice_locale: Locale to use for formatting
        
    Returns:
        Path to generated PDF file, or None if generation failed
    """
    try:
        # Set the locale
        locale.setlocale(locale.LC_ALL, invoice_locale)
    except locale.Error as e:
        logging.warning(f"Could not set locale to {invoice_locale}: {e}")

    # Validate invoice data
    logging.info("Loading and validating invoice data...")
    try:
        invoice_data = InvoiceData.model_validate_json(invoice_data_json)
    except ValidationError as ve:
        error_details = [
            f"/{'/'.join(map(str, e['loc']))}: {e['type']}, {e['msg']}"
            for e in ve.errors()
        ]
        logging.error(f"Invoice data validation failed: {error_details}")
        return None

    return write_invoice(invoice_data)


def rdf_metadata_generator() -> bytes:
    """Generate RDF metadata for the PDF."""
    # Note: rdf_xml_root is not defined in this code - this needs to be fixed
    # For now, returning empty metadata
    logging.warning("RDF metadata generator not properly implemented")
    return b"<?xml version='1.0' encoding='UTF-8'?><rdf:RDF xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'></rdf:RDF>"


def load_css_content(css_path: Path) -> str:
    """Load CSS content from file."""
    try:
        return css_path.read_text(encoding='utf-8')
    except FileNotFoundError:
        logging.error(f"CSS file not found: {css_path}")
        raise
    except Exception as e:
        logging.error(f"Error reading CSS file {css_path}: {e}")
        raise


def render_html_template(template_data: dict) -> str:
    """Render the HTML template with the provided data."""
    try:
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template('html/invoice.html')
        return template.render(template_data)
    except TemplateNotFound as e:
        logging.error(f"Template not found: {e}")
        raise
    except Exception as e:
        logging.error(f"Error rendering template: {e}")
        raise


def write_invoice(invoice_data: InvoiceData) -> Optional[str]:
    """
    Write invoice data to PDF file.
    
    Args:
        invoice_data: Validated invoice data
        
    Returns:
        Path to generated PDF file, or None if generation failed
    """
    try:
        # Pre-process the data
        logging.info("Pre-processing invoice data...")
        data_processor = InvoiceDataProcessor(invoice_data)
        template_data = data_processor.get_template_data()

        # Generate Factur-X XML
        logging.info("Generating Factur-X XML document...")
        xml_tree = FacturXProcessor.generate_facturx_xml(
            data_processor.get_template_data(formatted=False)
        )

        # Load CSS
        css_path = Path('static/css/style.css')
        template_data["inline_css"] = load_css_content(css_path)

        # Render HTML template
        html_content = render_html_template(template_data)

        # Prepare output
        title = f"FACTURE N°{invoice_data.invoice_number} - {invoice_data.client_info.name}"
        # Sanitize filename
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_', '°')).rstrip()

        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        pdf_file_path = output_dir / f"{safe_title}.pdf"

        # Generate PDF
        logging.info(f"Generating PDF invoice at '{pdf_file_path}'...")
        pdf_document = HTML(string=html_content).render()

        # Prepare XML attachment
        xml_data = ET.tostring(
            xml_tree,
            xml_declaration=True,
            encoding='utf-8',
            pretty_print=True
        ).decode('utf-8')

        pdf_document.metadata.attachments = [
            Attachment(
                string=xml_data,
                base_url='factur-x.xml',
                description='Factur-x invoice',
            ),
        ]
        pdf_document.metadata.rdf_metadata_generator = rdf_metadata_generator
        pdf_document.write_pdf(str(pdf_file_path), pdf_variant='pdf/a-3b')

        # Set file permissions (more restrictive than 0o777)
        pdf_file_path.chmod(0o644)

        return str(pdf_file_path)

    except Exception as e:
        logging.error(f"Error generating PDF invoice: {e}")
        return None


def delete_pdf_file(file_path: str) -> None:
    """Delete a PDF file if it exists."""
    path = Path(file_path)
    try:
        if path.exists():
            path.unlink()
            logging.info(f"Deleted file: {file_path}")
        else:
            logging.warning(f"File not found: {file_path}")
    except Exception as e:
        logging.error(f"Error deleting file {file_path}: {e}")


def main():
    """Main function to handle command line execution."""
    setup_logging()

    if len(sys.argv) != 2:
        print("Usage: python main.py <invoice_data_file>")
        sys.exit(1)

    filename = Path(sys.argv[1])

    try:
        # Validate required files exist
        validate_file_paths()

        # Read and process invoice data
        if not filename.exists():
            logging.error(f"File '{filename}' not found.")
            sys.exit(1)

        content = filename.read_text(encoding='utf-8')
        pdf_invoice = generate_pdf_invoice(content)

        if pdf_invoice:
            logging.info(f"Successfully generated PDF invoice: '{pdf_invoice}'")
        else:
            logging.error("Failed to generate PDF invoice")
            sys.exit(1)

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
