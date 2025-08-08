# -*- coding: utf-8 -*-
{
    'name': "Serena Care - Gestión de Sexos",

    'summary': "Gestiona diferentes tipos de sexo con nombre único y abreviatura",

    'description': """
        Módulo para gestionar sexos con:
        - Nombre único (case-insensitive)
        - Abreviatura única en mayúsculas
    """,

    'author': 'Serena Care Team',
    'website': 'https://www.serena-care.mx',
    'license': 'LGPL-3',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Tools',
    'version': '18.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sc_group'],

    # always loaded
    "data": [
        "security/ir.model.access.csv", 
        "data/data_sex.xml",
        "views/res_sex_views.xml",
        "views/view_menu.xml",
    ],
    # only loaded in demonstration mode
    'demo': [],
    'assets': {
        'web.assets_backend': [
            'sc_sex/static/src/css/form_style.css',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 1,
   
}

