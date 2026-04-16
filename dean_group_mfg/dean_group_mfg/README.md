# Dean Group International — Odoo 17 Module
### Built by Zenvora | dean_group_mfg

---

## What This Module Does

Complete Odoo ERP for Dean Group International Ltd (Manchester, UK).
Replaces: MS Access database, Sage, WordPress website, spreadsheets, email-only CRM.

### Modules Activated
| Module | Replaces |
|---|---|
| Odoo Website (homepage at `/`) | WordPress site |
| Manufacturing MRP | MS Access production DB |
| Inventory (multi-warehouse) | Spreadsheets |
| CRM + Casting Enquiries | Outlook email |
| Quality Inspections + Multilingual CoC | Paper forms |
| HR + Payroll + Attendance | Payroll bureau + Excel |
| Purchase + China Supply Orders | Email + WeChat |
| Maintenance (20 machines) | Paper log |
| Recruitment / Careers | Word docs + email |
| Accounting (UK MTD VAT) | Sage |

---

## Installation

### Requirements
- Odoo 17 Community or Enterprise
- Python 3.10+
- Ubuntu 22.04 recommended

### Steps

```bash
# 1. Copy module to your Odoo addons path
cp -r dean_group_mfg /opt/odoo/addons/

# 2. Restart Odoo
sudo systemctl restart odoo

# 3. In Odoo: Settings → Activate Developer Mode
# 4. Apps → Update Apps List
# 5. Search "Dean Group" → Install

# Demo data loads automatically on install
```

### Python dependencies (standard - no extras needed)
All dependencies are standard Odoo modules.

---

## File Structure

```
dean_group_mfg/
├── __manifest__.py          # Module definition
├── __init__.py
│
├── models/
│   ├── casting.py           # CastingProcess, CastingEnquiry, WorkOrder ext
│   ├── quality.py           # QualityInspection
│   ├── hr_foundry.py        # FoundryEmployee, JobApplication ext
│   └── china_supply.py      # ChinaSupplyOrder
│
├── controllers/
│   └── website.py           # All website routes (/, /services, /markets etc)
│
├── views/
│   ├── casting_views.xml    # Casting enquiry kanban/list/form
│   ├── quality_views.xml    # Quality inspection views + search
│   ├── hr_foundry_views.xml # Employee foundry tab + lists
│   ├── china_supply_views.xml # China supply views
│   ├── menu.xml             # ALL backend menus (Dean Group sidebar)
│   ├── website_homepage.xml # Odoo website homepage template
│   ├── website_services.xml # /services, /markets, /careers, /contact, /get-quote
│   └── website_templates.xml # Shared: footer, 404, about, quality, terms, privacy
│
├── data/
│   ├── sequences.xml        # Auto-reference sequences
│   ├── company_data.xml     # Workcenters (IC, DC, AL, CNC, QI, PD)
│   ├── casting_processes.xml # 7 casting process records
│   ├── customers_vendors.xml # 20 customers + 20 vendors + 20 employees
│   ├── quality_data.xml     # 20 quality inspections + 20 CRM leads + 6 jobs
│   ├── maintenance_data.xml # 20 foundry machine records
│   └── website_data.xml     # Odoo website config + 9 nav menu items
│
├── reports/
│   ├── quality_cert_report.xml   # Multilingual CoC PDF (EN/ZH/DE/FR/AR)
│   ├── casting_delivery_note.xml # Delivery note PDF
│   └── payroll_report.xml        # Payslip PDF
│
├── security/
│   ├── groups.xml           # Dean Group / User, Manager groups
│   └── ir.model.access.csv  # Access rights
│
└── static/src/
    ├── css/
    │   ├── website.css      # Full frontend CSS (dark foundry theme)
    │   └── backend.css      # Backend tweaks
    └── js/
        └── website.js       # Scroll reveal + Odoo public widget
```

---

## Website Pages (Odoo Frontend)

| URL | Template | Description |
|---|---|---|
| `/` | `homepage` | Main homepage with processes pulled from DB |
| `/services` | `services_page` | All casting processes dynamically listed |
| `/markets` | `markets_page` | 7 industry sectors with descriptions |
| `/about` | `about_page` | Company history + timeline |
| `/quality` | `quality_page` | ISO certs + QA process steps |
| `/careers` | `careers_page` | Live jobs from `hr.job` records |
| `/contact` | `contact_page` | Contact form → creates CRM lead |
| `/get-quote` | `quote_page` | Quote request form → creates CRM lead |
| `/terms-and-conditions` | `terms_page` | Legal terms |
| `/privacy-policy` | `privacy_page` | GDPR privacy policy |

---

## Backend Menus (Odoo Sidebar)

```
Dean Group (app)
├── Sales & Enquiries
│   ├── Casting Enquiries (Kanban + List + Form)
│   ├── CRM Pipeline
│   ├── Sales Orders
│   └── Customers
├── Manufacturing
│   ├── Manufacturing Orders
│   ├── Work Centres
│   ├── Casting Processes
│   └── Bills of Materials
├── Inventory & Supply
│   ├── Products
│   ├── Stock Movements
│   ├── Purchase Orders
│   ├── Suppliers / Vendors
│   ├── China Supply Orders
│   └── Orders In Transit
├── Quality
│   ├── All Inspections
│   └── Pending Certificates
├── HR & People
│   ├── Foundry Employees
│   ├── Apprentices
│   ├── Leave Management
│   ├── Attendance & Shifts
│   ├── Payroll
│   └── Recruitment
├── Maintenance
│   ├── Equipment (20 machines)
│   └── Maintenance Requests
├── Accounting
│   ├── Customer Invoices
│   ├── Vendor Bills
│   └── Bank & Cash
└── Website
    ├── View Homepage
    ├── Website Editor
    └── News / Blog
```

---

## Reports Available

| Report | Model | Languages |
|---|---|---|
| Certificate of Conformity | `dg.quality.inspection` | EN, 中文, DE, FR, AR |
| Casting Delivery Note | `stock.picking` | EN |
| Payslip | `hr.payslip` | EN |

To print a multilingual CoC:
1. Open a Quality Inspection record
2. Set **Certificate Language** field
3. Click **Print → Certificate of Conformity**

---

## Demo Data Loaded on Install

| Model | Records |
|---|---|
| Casting Processes | 7 |
| Employees | 20 (UK foundry staff) |
| Customers | 20 (Rolls-Royce, BAE, Airbus etc) |
| Suppliers/Vendors | 20 (UK + China) |
| Quality Inspections | 20 |
| CRM Leads | 20 |
| Maintenance Equipment | 20 foundry machines |
| Job Vacancies | 6 |
| Work Centres | 6 |

---

## Customisation Notes

- **Chrome version**: Set `CHROME_VERSION` in scraper if Chrome updates
- **Odoo website**: Go to `Website → Edit` to use drag-and-drop on any page
- **Add products**: Edit `data/product_data.xml` and re-upgrade module
- **Multi-company**: China company auto-created; assign users in Settings
- **Email**: Configure outgoing mail server in Settings → Technical → Email

---

## Support

Built by **Zenvora** | www.zenvora.com | contact@zenvora.com

For Odoo implementation, support retainer or further development:
- Email: contact@zenvora.com
- Server: Hetzner CX41 (recommended) — £16/month
- Odoo Community: Free (self-hosted)
