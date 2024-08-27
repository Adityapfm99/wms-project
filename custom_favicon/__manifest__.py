{
    'name': 'Custom Favicon & Theme',
    'version': '1.0',
    'category': 'Website',
    'author': 'Aditya',
    'summary': 'Custom Favicon for Odoo based on Company',
    'description': """
       
    """,
    'depends': ['stock','web'],
    'data': [ 
        'views/res_company_views.xml',
        'views/assets.xml',
        'views/custom_login_template.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'custom_favicon/static/src/js/custom_title.js',
            'custom_favicon/static/src/scss/custom_header.scss',
        ],
    },
    'images': ['static/description/img.png'],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
    'price': 2,
    'currency': 'USD',
}
