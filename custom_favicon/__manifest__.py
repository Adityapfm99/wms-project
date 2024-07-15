{
    'name': 'Custom Favicon',
    'version': '1.0',
    'category': 'Website',
    'author': 'Aditya',
    'summary': 'Custom Favicon for Odoo based on Company',
    'description': 'This module allows each company to have its own custom favicon in Odoo.',
    'depends': ['stock','web'],
    'data': [
        'views/res_company_views.xml',
        'views/assets.xml',
        'views/custom_login_template.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'custom_favicon/static/src/js/custom_title.js',
        ],
    },
    
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
