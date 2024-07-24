{
    'name': 'Farming Management',
    'version': '17.0.1.0',
    'category': 'Farming Agriculture',
    'author': 'Aditya',
    'summary': 'Comprehensive management solution for agriculture and farming.',
    'description': """
        <div>
            <h2>Custom Agriculture Management</h2>
            <p>This module provides tools to manage farms, crops, livestock, equipment, and sales in a unified system.</p>
            <h3>Features:</h3>
            <ul>
                <li>Farm and Crop Management</li>
                <li>Livestock Tracking</li>
                <li>Equipment Maintenance</li>
                <li>Inventory and Sales Management</li>
                <li>Detailed Reporting and Analytics</li>
            </ul>
            <img src="/farming_management/static/description/farming.png" alt="Farming Agriculture Management" style="max-width: 100%;"/>
        </div>
    """,
    'depends': ['base','stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/farm_views.xml',
        'views/crop_views.xml', 
        'views/equipment_views.xml',
        'views/res_users_views.xml',
        'views/bom_views.xml',
        'views/crop_analysis_views.xml', 
        'reports/crop_reports.xml',      
        'views/crop_report_template.xml',
        'data/initial_data.xml',
    ],
    'images': ['farming_management/static/description/tractors.png'],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
    'price': 50,
    'currency': 'USD',
}
