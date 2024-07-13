{
    'name': 'Custom User Stock Locations',
    'version': '1.0',
    'category': 'Custom',
    'author': 'Aditya',
    'summary': 'Allow users to select multiple stock locations',
    'depends': ['base', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_users_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
