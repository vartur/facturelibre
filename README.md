# 📄 FactureLibre — Professional invoicing for French micro-entrepreneurs

🇫🇷 **Simplify your invoicing. Stay compliant.**

**FactureLibre** is a lightweight yet powerful tool tailored for French micro-entrepreneurs. It streamlines invoice
creation while ensuring full compliance with French tax laws and European e-invoicing standards.

🇪🇺 Built with [pyfactx](https://github.com/vartur/pyfactx), it generates PDF A/3 invoices compatible with the **Factur-X** / **ZUGFeRD** (**EN 16931**)
standard.

## 🚀 Features

* ✅ Generates legally compliant invoices for French micro-entrepreneurs
* 🧾 Supports **Factur-X** / **ZUGFeRD** (EN 16931) e-invoicing format
* 📎 Outputs both human-readable PDF and embedded XML
* 🪶 Lightweight and easy to use — perfect for freelancers and small businesses

## 🛠️ Installation

Clone the repository and install the required dependencies:

```bash
git clone git@github.com:vartur/facturelibre.git
cd facturelibre
pip install -r requirements.txt
```

## ⚙️ Usage

To generate an invoice from a structured JSON file:

```bash
python main.py <path_to_invoice_data.json>
```

Make sure your JSON file contains all the required invoice data. An example is provided
in [invoice_data.json](./invoice_data.json)

## 📜 License

This project is licensed under the MIT License.
