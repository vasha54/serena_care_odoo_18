# -*- coding: utf-8 -*-
{
    'name': "sc_uom",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'uom',
        'product',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/data_uom_unit.xml',
        'data/data_uom_time.xml',
        'data/data_uom_medicament.xml',
        'data/data_uom_weight.xml', 
        'data/data_uom_volumen.xml',
        'data/data_uom_length.xml', 
        'views/uom_categories_views.xml',
        'views/uom_units_views.xml',
        'views/view_menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 1,
}

