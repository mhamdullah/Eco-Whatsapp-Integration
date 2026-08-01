# -*- coding: utf-8 -*-

import hmac
import hashlib
from odoo import http
from odoo.http import request

class EcoWhatsAppPortal(http.Controller):

    def _verify_token(self, model, res_id, token):
        """ Verifies HMAC token using database UUID """
        if not token:
            return False
        secret = request.env['ir.config_parameter'].sudo().get_param('database.uuid') or 'eco_secret_key'
        message = f"{model}-{res_id}"
        expected_token = hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected_token, token)

    @http.route('/pos/receipt/<int:order_id>', type='http', auth='public', website=True)
    def pos_receipt_portal(self, order_id, access_token=None, **kw):
        """ Render secure public ticket view for POS order """
        if not self._verify_token('pos.order', order_id, access_token):
            return "Access Denied: Invalid or missing token."

        order = request.env['pos.order'].sudo().browse(order_id)
        if not order.exists():
            return "POS Receipt not found."

        return request.render('eco_whatsapp_integration.pos_receipt_portal_template', {
            'order': order,
            'company': order.company_id,
        })

    @http.route('/my/payslip/<int:payslip_id>', type='http', auth='public', website=True)
    def payslip_portal(self, payslip_id, access_token=None, **kw):
        """ Render secure public payslip view for employee """
        if not self._verify_token('hr.payslip', payslip_id, access_token):
            return "Access Denied: Invalid or missing token."

        payslip = request.env['hr.payslip'].sudo().browse(payslip_id)
        if not payslip.exists():
            return "Payslip not found."

        return request.render('eco_whatsapp_integration.payslip_portal_template', {
            'payslip': payslip,
            'employee': payslip.employee_id,
            'company': payslip.company_id,
        })
