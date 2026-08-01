# -*- coding: utf-8 -*-

from odoo import models, fields, api

class EcoWhatsAppLog(models.Model):
    _name = 'eco.whatsapp.log'
    _description = 'Eco WhatsApp Audit Log'
    _order = 'create_date desc'

    create_date = fields.Datetime(string="Datetime", readonly=True, default=fields.Datetime.now)
    user_id = fields.Many2one('res.users', string="User", readonly=True, default=lambda self: self.env.user)
    partner_id = fields.Many2one('res.partner', string="Customer/Supplier", readonly=True)
    phone_number = fields.Char(string="Phone Number", readonly=True)
    document_type = fields.Selection([
        ('invoice', 'Customer Invoice'),
        ('credit_note', 'Customer Credit Note'),
        ('bill', 'Vendor Bill'),
        ('vendor_credit_note', 'Vendor Credit Note'),
        ('statement', 'Customer Statement'),
        ('quotation', 'Quotation'),
        ('sale_order', 'Sales Order'),
        ('picking', 'Delivery Order'),
        ('purchase_rfq', 'Request for Quotation'),
        ('purchase_order', 'Purchase Order'),
        ('payslip', 'Payslip'),
        ('pos_order', 'POS Receipt'),
        ('contact', 'Contact Form'),
    ], string="Document Type", readonly=True)
    document_ref = fields.Char(string="Document Reference", readonly=True)
    status = fields.Selection([
        ('draft_opened', 'Draft Opened'),
        ('sent_manually', 'Sent Manually'),
        ('failed', 'Failed'),
    ], string="Status", readonly=True, default='draft_opened')
    company_id = fields.Many2one('res.company', string="Company", readonly=True, default=lambda self: self.env.company)

    @api.model
    def _get_document_type(self, model, res_id, doc_type):
        """ Map internal doc_type to allowed selection values """
        if doc_type == 'sale' and model == 'sale.order':
            record = self.env[model].browse(res_id)
            if record.exists() and record.state in ('draft', 'sent'):
                return 'quotation'
            return 'sale_order'
        elif doc_type == 'purchase' and model == 'purchase.order':
            record = self.env[model].browse(res_id)
            if record.exists() and record.state in ('draft', 'sent', 'to approve'):
                return 'purchase_rfq'
            return 'purchase_order'
        elif doc_type == 'pos' and model == 'pos.order':
            return 'pos_order'
        return doc_type

