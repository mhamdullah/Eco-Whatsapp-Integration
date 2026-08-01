# -*- coding: utf-8 -*-

import re
import urllib.parse
import hmac
import hashlib
from odoo import models, fields, _
from odoo.exceptions import UserError

class EcoWhatsAppMixin(models.AbstractModel):
    _name = 'eco.whatsapp.mixin'
    _description = 'Eco WhatsApp Mixin'

    def _get_whatsapp_number(self):
        """ Get the partner's phone number following priority: Mobile -> Phone -> Parent Company Phone """
        self.ensure_one()
        phone = False
        
        # HR Payslip handling
        if self._name == 'hr.payslip' and self.employee_id:
            phone = self.employee_id.mobile_phone or self.employee_id.work_phone
            if not phone and self.employee_id.address_home_id:
                phone = self.employee_id.address_home_id.mobile or self.employee_id.address_home_id.phone
        else:
            partner = getattr(self, 'partner_id', False) or (self if self._name == 'res.partner' else False)
            if self._name == 'pos.order' and not partner:
                partner = self.partner_id
            
            if partner:
                phone = partner.mobile or partner.phone
                if not phone and partner.parent_id:
                    phone = partner.parent_id.mobile or partner.parent_id.phone
                    
        return self._clean_whatsapp_number(phone)

    def _clean_whatsapp_number(self, number):
        """ Clean phone number to keep only digits and optional '+' sign """
        if not number:
            return False
        # Keep only digits and '+'
        cleaned = re.sub(r'[^\d+]', '', number)
        # Ensure it contains at least one digit
        if not re.search(r'\d', cleaned):
            return False
        return cleaned

    def _get_whatsapp_access_token(self):
        """ Generate a secure HMAC token for public links using database UUID as secret key """
        self.ensure_one()
        secret = self.env['ir.config_parameter'].sudo().get_param('database.uuid') or 'eco_secret_key'
        message = f"{self._name}-{self.id}"
        return hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()

    def _get_document_url(self):
        """ Generate the document URL (public/portal share link or backend/custom controller link) """
        self.ensure_one()
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url') or ''
        
        # Check settings
        company = self.env.company
        if not company.eco_wa_enable_doc_links:
            return ""

        # Check if portal.mixin is inherited or custom portal controllers
        if hasattr(self, 'get_portal_url'):
            try:
                portal_url = self.get_portal_url()
                return f"{base_url.rstrip('/')}{portal_url}"
            except Exception:
                pass
                
        # Custom models: hr.payslip or pos.order or fallback
        token = self._get_whatsapp_access_token()
        if self._name == 'hr.payslip':
            return f"{base_url.rstrip('/')}/my/payslip/{self.id}?access_token={token}"
        elif self._name == 'pos.order':
            return f"{base_url.rstrip('/')}/pos/receipt/{self.id}?access_token={token}"
            
        # Fallback to standard backend link (requires login)
        return f"{base_url.rstrip('/')}/web#id={self.id}&model={self._name}&view_type=form"

    def _get_wa_placeholders(self, doc_type):
        """ Returns dictionary of all placeholders and their values for this record """
        self.ensure_one()
        company = self.env.company

        # Common values
        partner_name = ""
        partner = getattr(self, 'partner_id', False) or (self if self._name == 'res.partner' else False)
        if self._name == 'hr.payslip' and self.employee_id:
            partner_name = self.employee_id.name
        elif self._name == 'pos.order' and not partner:
            partner = self.partner_id
            
        if partner:
            partner_name = partner.name
            
        employee_name = getattr(self, 'employee_id', False).name if getattr(self, 'employee_id', False) else ""
        company_name = company.name or self.env.user.company_id.name or ""
        
        doc_date = ""
        # Date lookups
        for field in ['date_invoice', 'invoice_date', 'date_order', 'date', 'create_date', 'date_to']:
            if getattr(self, field, False):
                val = getattr(self, field)
                if isinstance(val, fields.Date) or isinstance(val, fields.Datetime):
                    doc_date = val.strftime('%d-%b-%Y')
                else:
                    doc_date = str(val)
                break

        # Totals
        subtotal = "0.00"
        tax = "0.00"
        total = "0.00"
        
        if hasattr(self, 'amount_untaxed'):
            subtotal = f"{self.amount_untaxed:,.2f}"
        if hasattr(self, 'amount_tax'):
            tax = f"{self.amount_tax:,.2f}"
        if hasattr(self, 'amount_total'):
            total = f"{self.amount_total:,.2f}"

        # Items details
        items_str = ""
        enable_item_details = company.eco_wa_enable_item_details
        enable_tax = company.eco_wa_enable_tax_display
        
        lines = []
        if self._name == 'account.move':
            lines = self.invoice_line_ids.filtered(lambda l: l.display_type not in ('line_section', 'line_note'))
        elif self._name == 'sale.order':
            lines = self.order_line.filtered(lambda l: not l.display_type)
        elif self._name == 'purchase.order':
            lines = self.order_line.filtered(lambda l: not l.display_type)
        elif self._name == 'stock.picking':
            lines = self.move_ids_without_package
        elif self._name == 'pos.order':
            lines = self.lines
            
        if lines:
            if enable_item_details:
                for idx, line in enumerate(lines, 1):
                    # Quantities
                    qty = getattr(line, 'quantity', False) or getattr(line, 'product_uom_qty', False) or getattr(line, 'qty', False) or getattr(line, 'product_qty', 0)
                    # Prices
                    price = getattr(line, 'price_unit', 0)
                    # Line subtotal
                    price_subtotal = getattr(line, 'price_subtotal', qty * price)
                    
                    product_name = line.product_id.display_name or line.name or "Product"
                    items_str += f"{idx}. {product_name}\n   Qty: {qty}\n   Unit Price: {price:,.2f}\n   Amount: {price_subtotal:,.2f}\n\n"
            else:
                for line in lines:
                    product_name = line.product_id.display_name or line.name or "Product"
                    items_str += f"* {product_name}\n"
        
        # Payslip specific
        net_salary = ""
        if self._name == 'hr.payslip':
            net_rule = self.line_ids.filtered(lambda l: l.code == 'NET')
            net_salary = f"{net_rule[0].total:,.2f}" if net_rule else "0.00"
            # basic rule
            basic_rule = self.line_ids.filtered(lambda l: l.code == 'BASIC')
            subtotal = f"{basic_rule[0].total:,.2f}" if basic_rule else "0.00"
            # date format for payslip is month name
            date_to = getattr(self, 'date_to', False)
            if date_to:
                doc_date = date_to.strftime('%B %Y')

        # Formatting values
        return {
            'partner_name': partner_name or "Valued Customer",
            'invoice_number': getattr(self, 'name', '') or '',
            'bill_number': getattr(self, 'ref', '') or getattr(self, 'name', '') or '',
            'receipt_number': getattr(self, 'pos_reference', '') or getattr(self, 'name', '') or '',
            'date': doc_date,
            'items': items_str.strip(),
            'subtotal': subtotal,
            'tax': tax if enable_tax else "",
            'total': total,
            'employee_name': employee_name or partner_name or "",
            'net_salary': net_salary,
            'document_url': self._get_document_url() or "",
            'company_name': company_name,
        }

    def _get_whatsapp_message(self, doc_type):
        """ Compiles the WhatsApp template with record specific placeholder values """
        self.ensure_one()
        company = self.env.company
        
        # Get template content from company configuration
        template_field = f"eco_wa_template_{doc_type}"
        template_text = getattr(company, template_field, False)
        
        # Fallback to general contact template
        if not template_text:
            template_text = company.eco_wa_template_contact or "Dear {{partner_name}},\n\nRegards,\n{{company_name}}"

        placeholders = self._get_wa_placeholders(doc_type)
        rendered = template_text
        
        # Custom Placeholder Replacement
        for key, val in placeholders.items():
            rendered = rendered.replace(f"{{{{{key}}}}}", str(val or ""))

        # Append company signature if configured and signature placeholder/toggles
        if company.eco_wa_signature:
            sig = company.eco_wa_signature.replace("{{company_name}}", placeholders['company_name'])
            if sig.strip() and sig.strip().lower() not in rendered.lower():
                rendered = rendered + "\n\n" + sig
        
        # Strip greeting if disabled
        if not company.eco_wa_enable_greeting:
            lines = rendered.split('\n')
            if lines and lines[0].strip().startswith("Dear"):
                rendered = '\n'.join(lines[1:]).strip()

        return rendered

    def action_send_whatsapp(self):
        """ Generates WhatsApp Web draft link and returns direct redirect action """
        self.ensure_one()
        company = self.env.company
        if not company.eco_wa_enabled:
            raise UserError(_("WhatsApp Integration is disabled in Settings."))

        # 1. Phone number logic
        phone = self._get_whatsapp_number()
        if not phone:
            raise UserError(_("No valid phone or mobile number found for this partner/contact. Please make sure the number is in international format."))

        # 2. Determine document type key based on model
        doc_map = {
            'account.move': 'invoice' if (self._name == 'account.move' and self.move_type in ('out_invoice', 'out_refund')) else 'bill',
            'sale.order': 'sale',
            'purchase.order': 'purchase',
            'stock.picking': 'picking',
            'hr.payslip': 'payslip',
            'pos.order': 'pos',
            'res.partner': 'contact',
        }
        doc_type = doc_map.get(self._name, 'contact')
        
        # Custom adjustment for sub-types
        if self._name == 'account.move':
            if self.move_type == 'out_refund':
                doc_type = 'credit_note'
            elif self.move_type == 'in_refund':
                doc_type = 'vendor_credit_note'
            elif self._context.get('is_statement'):
                doc_type = 'statement'

        # 3. Message generation
        message = self._get_whatsapp_message(doc_type)
        encoded_message = urllib.parse.quote(message)
        
        whatsapp_url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_message}"

        # 4. Audit logging
        partner = False
        if self._name == 'res.partner':
            partner = self
        elif getattr(self, 'partner_id', False):
            partner = self.partner_id
        elif getattr(self, 'employee_id', False) and getattr(self.employee_id, 'address_home_id', False):
            partner = self.employee_id.address_home_id

        self.env['eco.whatsapp.log'].sudo().create({
            'partner_id': partner.id if partner else False,
            'phone_number': phone,
            'document_type': self.env['eco.whatsapp.log']._get_document_type(self._name, self.id, doc_type),
            'document_ref': getattr(self, 'name', '') or getattr(self, 'ref', '') or '',
            'status': 'draft_opened',
        })

        # Update Last Sent Date on Partner
        if partner:
            partner.sudo().write({'eco_wa_last_sent_date': fields.Datetime.now()})

        # 5. Chatter logging
        if hasattr(self, 'message_post'):
            try:
                self.message_post(body=_("WhatsApp draft generated and opened in browser tab for phone %s.") % phone)
            except Exception:
                pass

        # 6. Return action to open URL in a new window/tab
        return {
            'type': 'ir.actions.act_url',
            'url': whatsapp_url,
            'target': 'new',
        }

    def action_get_pos_whatsapp_url(self, phone):
        """ Generates WhatsApp Web draft link for POS receipt sharing """
        self.ensure_one()
        cleaned_phone = self._clean_whatsapp_number(phone)
        if not cleaned_phone:
            raise UserError(_("No valid phone number provided."))

        message = self._get_whatsapp_message('pos')
        encoded_message = urllib.parse.quote(message)
        whatsapp_url = f"https://web.whatsapp.com/send?phone={cleaned_phone}&text={encoded_message}"

        partner = getattr(self, 'partner_id', False) or (self if self._name == 'res.partner' else False)
        if self._name == 'pos.order' and not partner:
            partner = self.partner_id

        self.env['eco.whatsapp.log'].sudo().create({
            'partner_id': partner.id if partner else False,
            'phone_number': cleaned_phone,
            'document_type': 'pos_order',
            'document_ref': getattr(self, 'pos_reference', '') or getattr(self, 'name', '') or '',
            'status': 'draft_opened',
        })

        if partner:
            partner.sudo().write({'eco_wa_last_sent_date': fields.Datetime.now()})

        if hasattr(self, 'message_post'):
            try:
                self.message_post(body=_("WhatsApp POS receipt generated and opened in browser tab for phone %s.") % cleaned_phone)
            except Exception:
                pass

        return {'url': whatsapp_url}
