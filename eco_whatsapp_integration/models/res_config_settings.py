# -*- coding: utf-8 -*-

from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    eco_wa_enabled = fields.Boolean(string="Enable Eco WhatsApp Integration", default=True)
    
    # Templates
    eco_wa_template_invoice = fields.Text(string="Customer Invoice Template", default="""Dear {{partner_name}},

Thank you for your business.

Invoice No: {{invoice_number}}
Invoice Date: {{date}}

Items:
{{items}}

Subtotal: {{subtotal}}
Tax: {{tax}}
Total Amount: {{total}}

View Invoice:
{{document_url}}

Thank you.""")

    eco_wa_template_bill = fields.Text(string="Vendor Bill Template", default="""Dear Supplier,

Vendor Bill No: {{bill_number}}

Items:
{{items}}

Total Amount: {{total}}

View Bill:
{{document_url}}

Regards,
{{company_name}}""")

    eco_wa_template_sale = fields.Text(string="Quotation/Sales Order Template", default="""Dear {{partner_name}},

Please find attached details for Quotation/Order: {{invoice_number}}
Date: {{date}}

Items:
{{items}}

Subtotal: {{subtotal}}
Tax: {{tax}}
Total Amount: {{total}}

View Order:
{{document_url}}

Regards,
{{company_name}}""")

    eco_wa_template_purchase = fields.Text(string="Purchase Order Template", default="""Dear Supplier,

Please find attached Request for Quotation/Purchase Order No: {{bill_number}}
Date: {{date}}

Items:
{{items}}

Total Amount: {{total}}

View Order:
{{document_url}}

Regards,
{{company_name}}""")

    eco_wa_template_payslip = fields.Text(string="Payslip Template", default="""Dear {{employee_name}},

Salary Slip for {{date}}

Basic Salary: {{subtotal}}
Net Salary: {{net_salary}}

View Payslip:
{{document_url}}

Regards,
HR Department""")

    eco_wa_template_pos = fields.Text(string="POS Receipt Template", default="""Thank you for shopping with us.

Receipt No: {{receipt_number}}

Items:
{{items}}

Total Qty: {{subtotal}}
Total Amount: {{total}}

View Receipt:
{{document_url}}

Regards,
{{company_name}}""")

    eco_wa_template_contact = fields.Text(string="Contact Template", default="""Dear {{partner_name}},

How can we help you today?

Regards,
{{company_name}}""")

    # Configuration Toggles
    eco_wa_enable_doc_links = fields.Boolean(string="Enable Document Links", default=True)
    eco_wa_enable_tax_display = fields.Boolean(string="Enable Tax Display", default=True)
    eco_wa_enable_item_details = fields.Boolean(string="Enable Item Details", default=True)
    eco_wa_enable_greeting = fields.Boolean(string="Enable Customer Greeting", default=True)
    eco_wa_signature = fields.Text(string="Company Signature", default="Regards,\n{{company_name}}")


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    eco_wa_enabled = fields.Boolean(
        related='company_id.eco_wa_enabled',
        readonly=False,
        string="Enable Eco WhatsApp Integration"
    )
    
    # Templates
    eco_wa_template_invoice = fields.Text(
        related='company_id.eco_wa_template_invoice',
        readonly=False,
        string="Customer Invoice Template"
    )
    eco_wa_template_bill = fields.Text(
        related='company_id.eco_wa_template_bill',
        readonly=False,
        string="Vendor Bill Template"
    )
    eco_wa_template_sale = fields.Text(
        related='company_id.eco_wa_template_sale',
        readonly=False,
        string="Quotation/Sales Order Template"
    )
    eco_wa_template_purchase = fields.Text(
        related='company_id.eco_wa_template_purchase',
        readonly=False,
        string="Purchase Order/RFQ Template"
    )
    eco_wa_template_payslip = fields.Text(
        related='company_id.eco_wa_template_payslip',
        readonly=False,
        string="Payslip Template"
    )
    eco_wa_template_pos = fields.Text(
        related='company_id.eco_wa_template_pos',
        readonly=False,
        string="POS Receipt Template"
    )
    eco_wa_template_contact = fields.Text(
        related='company_id.eco_wa_template_contact',
        readonly=False,
        string="Contact/General Template"
    )

    # Configuration Toggles
    eco_wa_enable_doc_links = fields.Boolean(
        related='company_id.eco_wa_enable_doc_links',
        readonly=False,
        string="Enable Document Links"
    )
    eco_wa_enable_tax_display = fields.Boolean(
        related='company_id.eco_wa_enable_tax_display',
        readonly=False,
        string="Enable Tax Display"
    )
    eco_wa_enable_item_details = fields.Boolean(
        related='company_id.eco_wa_enable_item_details',
        readonly=False,
        string="Enable Item Details"
    )
    eco_wa_enable_greeting = fields.Boolean(
        related='company_id.eco_wa_enable_greeting',
        readonly=False,
        string="Enable Customer Greeting"
    )
    eco_wa_signature = fields.Text(
        related='company_id.eco_wa_signature',
        readonly=False,
        string="Company Signature"
    )
