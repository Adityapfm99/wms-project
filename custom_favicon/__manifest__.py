{
    'name': 'Custom Favicon',
    'version': '1.0',
    'category': 'Website',
    'author': 'Aditya',
    'summary': 'Custom Favicon for Odoo based on Company',
    'description': 'This module allows each company to have its own custom favicon in Odoo.',
    'depends': ['web'],
    'data': [
        'views/res_company_views.xml',
        'views/assets.xml',
    ],

    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
