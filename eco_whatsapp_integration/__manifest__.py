# -*- coding: utf-8 -*-
{
    'name': 'Eco WhatsApp Integration',
    'version': '18.0.1.0.0',
    'category': 'Sales/Accounting',
    'summary': 'Send Odoo documents via WhatsApp Web draft links without third-party API costs',
    'description': """
Eco WhatsApp Integration
========================
This module allows users to generate pre-filled WhatsApp messages for Odoo documents and opens them directly in WhatsApp Web.
The messages remain in draft mode so you can review and manually send them.

Supported Documents:
--------------------
* Accounting: Customer Invoices, Credit Notes, Vendor Bills, Vendor Credit Notes, Customer Statements
* Sales: Quotations, Sales Orders, Delivery Orders
* Purchase: Requests for Quotations, Purchase Orders, Vendor Bills
* Contacts: Contact Form, Customer Form, Vendor Form
* Payroll: Payslips, Employee Salary Statements (Compatible with Enterprise & Community custom payrolls)
* Point of Sale (POS): Interactive WhatsApp Send Popup after Order Validation

Features:
---------
* Message configuration & settings
* Clean phone number formatting (international format)
* Custom placeholders rendering
* Bulk WhatsApp draft generation via specialized wizard
* Chatter logging and full audit log of all sent attempts
* Secure public portal sharing URL generation for Payslips and POS receipts
""",
    'author': 'EcoBiz Bd',
    'website': 'https://ecobizbd.com',
    'depends': [
        'base',
        'mail',
        'portal',
        'account',
        'sale',
        'purchase',
        'stock',
        'point_of_sale',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/res_partner_views.xml',
        'views/account_move_views.xml',
        'views/sale_order_views.xml',
        'views/purchase_order_views.xml',
        'views/stock_picking_views.xml',
        'views/eco_whatsapp_log_views.xml',
        'wizards/bulk_send_wizard_views.xml',
        'views/templates.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'eco_whatsapp_integration/static/src/js/pos_whatsapp_popup.js',
            'eco_whatsapp_integration/static/src/xml/pos_whatsapp_popup.xml',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
}
