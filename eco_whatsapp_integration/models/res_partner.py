# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner', 'eco.whatsapp.mixin']

    eco_wa_number = fields.Char(
        string="WhatsApp Number",
        compute="_compute_eco_wa_number",
        store=True,
        help="Cleaned international format phone number used for WhatsApp."
    )
    eco_wa_last_sent_date = fields.Datetime(
        string="Last WhatsApp Sent",
        readonly=True,
        help="Date and time when the last WhatsApp draft was generated for this contact."
    )

    @api.depends('mobile', 'phone')
    def _compute_eco_wa_number(self):
        for partner in self:
            partner.eco_wa_number = partner._get_whatsapp_number() or ''
