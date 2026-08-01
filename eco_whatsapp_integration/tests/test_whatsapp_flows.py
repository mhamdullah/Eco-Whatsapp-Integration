# -*- coding: utf-8 -*-

import hmac
import hashlib
from odoo.tests.common import TransactionCase

class TestWhatsAppFlows(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestWhatsAppFlows, cls).setUpClass()
        # Setup company settings
        cls.company = cls.env.company
        cls.company.write({
            'eco_wa_enabled': True,
            'eco_wa_enable_greeting': True,
            'eco_wa_enable_item_details': True,
            'eco_wa_enable_tax_display': True,
            'eco_wa_enable_doc_links': True,
            'eco_wa_signature': "Regards,\n{{company_name}}",
        })

        # Create Partner
        cls.partner = cls.env['res.partner'].create({
            'name': 'John Doe',
            'mobile': '+880 1712-345 678',
            'phone': '123-456-789',
        })

        # Create Product
        cls.product = cls.env['product.product'].create({
            'name': 'Test Product A',
            'list_price': 100.0,
        })

    def test_01_number_sanitization(self):
        """ Test phone number cleaning utility """
        cleaned_mobile = self.partner._clean_whatsapp_number(self.partner.mobile)
        self.assertEqual(cleaned_mobile, '+8801712345678', "Failed to clean and parse mobile phone number.")

        cleaned_phone = self.partner._clean_whatsapp_number(self.partner.phone)
        self.assertEqual(cleaned_phone, '123456789', "Failed to clean and parse telephone number.")

        # Test priority helper
        num = self.partner._get_whatsapp_number()
        self.assertEqual(num, '+8801712345678', "Mobile number should have priority over Phone number.")

    def test_02_placeholder_formatting(self):
        """ Test that invoice templates correctly replace placeholders """
        # Create Invoice
        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.partner.id,
            'invoice_date': '2026-06-25',
            'invoice_line_ids': [
                (0, 0, {
                    'product_id': self.product.id,
                    'quantity': 2,
                    'price_unit': 100.0,
                    'name': 'Test Product A',
                })
            ]
        })

        placeholders = invoice._get_wa_placeholders('invoice')
        self.assertEqual(placeholders['partner_name'], 'John Doe')
        self.assertEqual(placeholders['date'], '25-Jun-2026')
        self.assertIn('Test Product A', placeholders['items'])
        self.assertIn('Qty: 2.0', placeholders['items'])

        # Message compiling check
        msg = invoice._get_whatsapp_message('invoice')
        self.assertIn('Dear John Doe,', msg)
        self.assertIn('Invoice Date: 25-Jun-2026', msg)
        self.assertIn('Test Product A', msg)
        self.assertIn('Regards,', msg)

    def test_03_audit_logging(self):
        """ Test that sending WhatsApp generates the correct audit log """
        initial_log_count = self.env['eco.whatsapp.log'].search_count([])

        # Trigger send action (which returns URL act_url action)
        res = self.partner.action_send_whatsapp()
        
        self.assertEqual(res['type'], 'ir.actions.act_url')
        self.assertIn('web.whatsapp.com', res['url'])

        # Check logs
        new_log_count = self.env['eco.whatsapp.log'].search_count([])
        self.assertEqual(new_log_count, initial_log_count + 1, "An audit log record should have been created.")

        latest_log = self.env['eco.whatsapp.log'].search([], limit=1)
        self.assertEqual(latest_log.partner_id, self.partner)
        self.assertEqual(latest_log.phone_number, '+8801712345678')
        self.assertEqual(latest_log.status, 'draft_opened')

    def test_04_portal_token_verification(self):
        """ Test secure access token generation and verification """
        token = self.partner._get_whatsapp_access_token()
        self.assertTrue(token)

        # Verify controller logic mock
        secret = self.env['ir.config_parameter'].sudo().get_param('database.uuid') or 'eco_secret_key'
        message = f"res.partner-{self.partner.id}"
        expected_token = hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()
        
        self.assertEqual(token, expected_token)

    def test_05_sale_order_whatsapp(self):
        """ Test that sending WhatsApp from sale.order works without AttributeError """
        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
        })
        res = sale_order.action_send_whatsapp()
        self.assertEqual(res['type'], 'ir.actions.act_url')
        self.assertIn('web.whatsapp.com', res['url'])

    def test_06_purchase_order_whatsapp(self):
        """ Test that sending WhatsApp from purchase.order works without AttributeError """
        purchase_order = self.env['purchase.order'].create({
            'partner_id': self.partner.id,
        })
        res = purchase_order.action_send_whatsapp()
        self.assertEqual(res['type'], 'ir.actions.act_url')
        self.assertIn('web.whatsapp.com', res['url'])

    def test_07_stock_picking_whatsapp(self):
        """ Test that sending WhatsApp from stock.picking works without AttributeError """
        picking_type = self.env['stock.picking.type'].search([], limit=1)
        picking = self.env['stock.picking'].create({
            'partner_id': self.partner.id,
            'picking_type_id': picking_type.id if picking_type else False,
        })
        res = picking.action_send_whatsapp()
        self.assertEqual(res['type'], 'ir.actions.act_url')
        self.assertIn('web.whatsapp.com', res['url'])


