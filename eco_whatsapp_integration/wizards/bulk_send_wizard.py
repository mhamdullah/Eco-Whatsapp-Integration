# -*- coding: utf-8 -*-

import urllib.parse
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class EcoWhatsAppBulkWizard(models.TransientModel):
    _name = 'eco.whatsapp.bulk.wizard'
    _description = 'Eco WhatsApp Bulk Send Wizard'

    line_ids = fields.One2many(
        'eco.whatsapp.bulk.wizard.line', 'wizard_id',
        string="Documents to Send"
    )

    @api.model
    def default_get(self, fields_list):
        res = super(EcoWhatsAppBulkWizard, self).default_get(fields_list)
        active_ids = self._context.get('active_ids')
        active_model = self._context.get('active_model')

        if not active_ids or not active_model:
            return res

        company = self.env.company
        if not company.eco_wa_enabled:
            raise UserError(_("WhatsApp Integration is disabled in Settings."))

        records = self.env[active_model].browse(active_ids)
        lines = []
        
        # Determine doc type key
        doc_map = {
            'account.move': 'invoice',
            'sale.order': 'sale',
            'purchase.order': 'purchase',
            'stock.picking': 'picking',
            'hr.payslip': 'payslip',
        }
        
        for record in records:
            # Check phone number
            phone = record._get_whatsapp_number()
            if not phone:
                continue

            # Determine doc type details
            doc_type = doc_map.get(active_model, 'contact')
            if active_model == 'account.move':
                if record.move_type == 'out_refund':
                    doc_type = 'credit_note'
                elif record.move_type == 'in_refund':
                    doc_type = 'vendor_credit_note'
                elif record.move_type in ('in_invoice', 'in_refund'):
                    doc_type = 'bill'
                elif self._context.get('is_statement'):
                    doc_type = 'statement'

            message = record._get_whatsapp_message(doc_type)
            encoded_message = urllib.parse.quote(message)
            whatsapp_url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_message}"

            partner = False
            if active_model == 'res.partner':
                partner = record
            elif getattr(record, 'partner_id', False):
                partner = record.partner_id
            elif getattr(record, 'employee_id', False) and getattr(record.employee_id, 'address_home_id', False):
                partner = record.employee_id.address_home_id
            partner_id = partner.id if partner else False

            lines.append((0, 0, {
                'res_model': active_model,
                'res_id': record.id,
                'partner_id': partner_id,
                'document_name': getattr(record, 'name', '') or getattr(record, 'ref', '') or f"{active_model} #{record.id}",
                'phone_number': phone,
                'whatsapp_url': whatsapp_url,
                'status': 'pending',
                'doc_type': doc_type,
            }))

        if not lines:
            raise UserError(_("None of the selected records had valid phone numbers or configuration for sending WhatsApp messages."))

        res['line_ids'] = lines
        return res


class EcoWhatsAppBulkWizardLine(models.TransientModel):
    _name = 'eco.whatsapp.bulk.wizard.line'
    _description = 'Eco WhatsApp Bulk Send Wizard Line'

    wizard_id = fields.Many2one('eco.whatsapp.bulk.wizard', string="Wizard")
    res_model = fields.Char(string="Model", required=True)
    res_id = fields.Integer(string="Record ID", required=True)
    partner_id = fields.Many2one('res.partner', string="Recipient")
    document_name = fields.Char(string="Document Ref")
    phone_number = fields.Char(string="Phone Number")
    whatsapp_url = fields.Char(string="WhatsApp URL")
    doc_type = fields.Char(string="Doc Type")
    status = fields.Selection([
        ('pending', 'Pending'),
        ('opened', 'Opened'),
    ], string="Status", default='pending')

    def action_send(self):
        """ Log audit, update status and open the WhatsApp Web tab """
        self.ensure_one()
        
        # Log audit entry
        self.env['eco.whatsapp.log'].sudo().create({
            'partner_id': self.partner_id.id if self.partner_id else False,
            'phone_number': self.phone_number,
            'document_type': self.env['eco.whatsapp.log']._get_document_type(self.res_model, self.res_id, self.doc_type or 'contact'),
            'document_ref': self.document_name,
            'status': 'draft_opened',
        })

        # Update Last Sent Date on Partner
        if self.partner_id:
            self.partner_id.sudo().write({'eco_wa_last_sent_date': fields.Datetime.now()})

        # Post message to document chatter if mail is inherited
        record = self.env[self.res_model].browse(self.res_id)
        if hasattr(record, 'message_post'):
            try:
                record.message_post(body=_("WhatsApp bulk draft generated and opened in browser tab for phone %s.") % self.phone_number)
            except Exception:
                pass

        # Update status in wizard
        self.write({'status': 'opened'})

        # Return action to open URL in a new window/tab and keep the wizard open
        return {
            'type': 'ir.actions.act_url',
            'url': self.whatsapp_url,
            'target': 'new',
        }
