{
    'name': 'Paie Planteur',
    'version': '1.0',
    'sequence': '-1',
    'summary': 'Summery',
    'description':"""
    Ce module facilite la gestion de la paie planteur dans Odoo
    - Lot de paie et calcule de faie de paie
    - Gestion des villages
    - Gestion de la paie par zone
    - Gestion des virements par zone
    - Rapport de suivi de paie
    - Generation automatique des ecritures comptables par periode paie
    - Configuration des journaux
    ====================================================
""",
    'category': 'Services/',
    'author': 'Mor Tall Seck',
    'website': 'https://www.integrateur.odoo.com',
    'depends': ['base','account'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'data/payroll_data.xml',
        'views/menu.xml',
        'wizard/import_bascule.xml',
        'wizard/plantation.xml',
        'wizard/prime_wizard_view.xml',
        'views/config.xml',
        'views/partner.xml',
        'views/plantation.xml',
        'views/category.xml',
        'views/rule.xml',
        'views/payslip.xml',
        'views/virement.xml',
        'views/prime_menu.xml',
        'views/prime_view.xml',
        'report/report_farmer.xml',
        'report/payment_report.xml',
        'report/reports.xml',
        'report/report_planting.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False
}
