# -*- coding: utf-8 -*-
{
    'name': 'Eco WhatsApp Integration - Enterprise Payroll Bridge',
    'version': '18.0.1.0.0',
    'category': 'Human Resources/Payroll',
    'summary': 'Bridge module to link Eco WhatsApp Integration with Enterprise Payroll',
    'description': """
Eco WhatsApp Integration - Enterprise Payroll Bridge
====================================================
Adds the "Send via WhatsApp" button on employee payslips for databases using the Enterprise Payroll module (hr_payroll).
    """,
    'author': 'EcoBiz Bd',
    'website': 'https://ecobizbd.com',
    'depends': [
        'eco_whatsapp_integration',
        'hr_payroll',
    ],
    'data': [
        'views/hr_payslip_views.xml',
    ],
    'auto_install': True,
    'installable': True,
    'license': 'LGPL-3',
}
