# -*- coding: utf-8 -*-

import logging
from odoo import models

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _name = 'account.move'
    _inherit = ['account.move', 'eco.whatsapp.mixin']

class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = ['sale.order', 'eco.whatsapp.mixin']

class StockPicking(models.Model):
    _name = 'stock.picking'
    _inherit = ['stock.picking', 'eco.whatsapp.mixin']

class PurchaseOrder(models.Model):
    _name = 'purchase.order'
    _inherit = ['purchase.order', 'eco.whatsapp.mixin']

class PosOrder(models.Model):
    _name = 'pos.order'
    _inherit = ['pos.order', 'eco.whatsapp.mixin']
