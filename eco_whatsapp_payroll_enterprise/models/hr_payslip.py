# -*- coding: utf-8 -*-

from odoo import models

class HrPayslip(models.Model):
    _name = 'hr.payslip'
    _inherit = ['hr.payslip', 'eco.whatsapp.mixin']
