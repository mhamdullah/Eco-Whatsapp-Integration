# -*- coding: utf-8 -*-

from odoo import models, api
from lxml import etree

class HrPayslip(models.Model):
    _name = 'hr.payslip'
    _inherit = ['hr.payslip', 'eco.whatsapp.mixin']

    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        res = super().get_view(view_id=view_id, view_type=view_type, **options)
        if view_type == 'form':
            try:
                doc = etree.fromstring(res['arch'])
                headers = doc.xpath('//header')
                if headers:
                    existing_button = doc.xpath("//button[@name='action_send_whatsapp']")
                    if not existing_button:
                        button = etree.Element('button', {
                            'name': 'action_send_whatsapp',
                            'string': 'Send via WhatsApp',
                            'type': 'object',
                            'icon': 'fa-whatsapp',
                            'invisible': "state == 'cancel'"
                        })
                        headers[0].append(button)
                        res['arch'] = etree.tostring(doc, encoding='unicode')
            except Exception:
                pass
        return res
