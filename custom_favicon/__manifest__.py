{
    'name': 'Custom Favicon & Theme',
    'version': '1.0',
    'category': 'Website',
    'author': 'Mahesa Tech',
    'summary': 'Custom Favicon for Odoo based on Company',
    'description': """
        <div>
            <h2>Custom Favicon & Theme</h2>
            <p>This module allows each company to have its own custom favicon in Odoo. It also includes customization options for the login screen and backend theme.</p>
            <h3>Features:</h3>
            <ul>
                <li>Individual favicon for each company</li>
                <li>Customizable login screen template</li>
                <li>Enhanced backend theme with custom headers</li>
            </ul>
            <p>Ensure your brand identity is consistent across all aspects of your Odoo system with custom favicons and theme options.</p>
            <img src="/custom_favicon/static/description/img.png" alt="Custom Favicon & Theme" style="max-width: 100%;"/>
        </div>
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
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
    'price': 2,
    'currency': 'USD',
}
