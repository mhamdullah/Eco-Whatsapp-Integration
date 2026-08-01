# -*- coding: utf-8 -*-
{
    'name': 'Eco WhatsApp Integration - Community Payroll Bridge',
    'version': '18.0.1.0.0',
    'category': 'Human Resources/Payroll',
    'summary': 'Bridge module to link Eco WhatsApp Integration with Community Payroll',
    'description': """
Eco WhatsApp Integration - Community Payroll Bridge
===================================================
Adds the "Send via WhatsApp" button on employee payslips for databases using the Community Payroll module (hr_payroll_community).
    """,
    'author': 'EcoBiz Bd',
    'website': 'https://ecobizbd.com',
    'depends': [
        'eco_whatsapp_integration',
        'hr_payroll_community',
    ],
    'data': [
        'views/hr_payslip_views.xml',
    ],
    'auto_install': True,
    'installable': True,
    'license': 'LGPL-3',
}
