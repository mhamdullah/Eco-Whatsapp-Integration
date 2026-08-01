# Eco-Whatsapp-Integration
Eco WhatsApp Integration
Odoo 18 Addon Installation Guide & User Manual

# Part 1: Installation Guide
Prerequisites
Odoo Version: Odoo v18 (Community or Enterprise edition).
Access Rights: Administrator privileges to install modules in the database.
Step-by-Step Installation
Extract the Files: Copy the eco_whatsapp_integration directory into your custom Odoo addons path folder.
Restart Odoo Server: Restart your Odoo service so that the new addon folder is detected by the server:
sudo service odoo-server restart
Enable Developer Mode: Log into your Odoo instance, navigate to Settings, and click Activate Developer Mode at the bottom of the page.
Update Apps List: Go to the Apps module and click on Update Apps List in the top header.
Install the Module: Search for Eco WhatsApp Integration in the search bar, remove the default Apps filter if necessary, and click Install.

# Part 2: Module Configuration
Once installed, configure settings under the main menu:

Settings > Eco WhatsApp or Eco WhatsApp > Settings

Configuration Options
Enable/Disable: Master switch to activate or deactivate the WhatsApp draft generation workflow.
Greetings: When enabled, automatically starts drafts with Dear [Customer Name],.
Item Details: When active, lists line items including Quantity, Unit Price, and line totals. When disabled, only a simple bulleted name list is printed.
Tax Display: Enables the display of VAT/Taxes in the total breakdowns.
Document Portal Links: Appends a secure sharing link (Portal URL) to invoices, bills, orders, receipts, and payslips.
Company Signature: Configures the closing text appended to the bottom of all drafts.
Supported Placeholders
Placeholder	Description	Example Value
{{partner_name}}	Name of the Customer / Supplier	John Doe
{{invoice_number}}	Reference code of Customer Invoices / Quotation	INV/2026/0001
{{bill_number}}	Reference code of Vendor Bills / RFQ	BILL/2026/0002
{{receipt_number}}	Point of Sale Order ticket reference	POS/2026/01/01
{{date}}	Document date (formated as DD-MMM-YYYY)	25-Jun-2026
{{items}}	Formatted string of products/line items	1. Product A (Qty: 2...)
{{subtotal}}	Amount before tax / basic salary for payslips	1,200.00
{{tax}}	Taxes total amount	120.00
{{total}}	Grand total amount	1,320.00
{{employee_name}}	Employee name for Payslip documents	Jane Smith
{{net_salary}}	Take home salary total	3,500.00
{{document_url}}	Secure Portal Link to view online	https://portal.company.com/my/invoice/123
{{company_name}}	Your current company name	Eco Industries
# Part 3: User Manual
Sending Documents via Backend
For all supported records (Invoices, Quotations, Purchase Orders, Delivery Orders, Payslips, Contacts), a Send via WhatsApp button will be visible in the header bar:

Click the Send via WhatsApp button.
Odoo will check for a valid Mobile or Phone number (falling back to parent company number if empty).
A new browser tab will open redirecting to https://web.whatsapp.com pre-filled with the message template.
Review the draft in WhatsApp and manually press Send.
Bulk WhatsApp Sending
From the list views of Customer Invoices, Vendor Bills, Sales Orders, or Purchase Orders:

Select multiple records using checkboxes on the left.
Click the **Actions** dropdown menu (cog icon) and select Send via WhatsApp.
A popup wizard opens showing all selected records, target phones, and statuses.
Click Open WhatsApp for each item to launch tabs sequentially without being blocked by browser popup-blockers.
POS Order Validation Dialog
After clicking "Validate" in Point of Sale, a modal popup will display options:

Send via WhatsApp: Prompts or allows verifying the customer's phone number, then opens WhatsApp Web with the ticket details and secure ticket viewing URL.
Print Receipt: Triggers standard ticket printing.
Close: Closes the popup and clears POS cart for the next customer.
Audit Logging
To inspect all sent attempts, navigate to Eco WhatsApp > Audit Logs. This records the timestamp, user, customer, document reference, and phone number of each draft generated.

© 2026 Eco WhatsApp Integration Addon. All rights reserved by EcoBiz Bd.
