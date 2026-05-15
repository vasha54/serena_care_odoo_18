# -*- coding: utf-8 -*-
{
    'name': "Serena Care - Notas de enfermerias",

    'summary': "Gestionar notas de enfermerías para residentes",

    'description': """
Módulo de Notas de Enfermería
        =============================
        Este módulo permite crear y gestionar notas de enfermerías asociadas a residentes.
    """,

    'author': 'Serena Care Team',
    'website': 'https://www.serena-care.mx',
    'license': 'LGPL-3',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'version': '18.0.1.0.0',
    'category': 'Productivity',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'sc_base',
        'sc_group',
        'sc_resident',
        'sc_employee',
    ],

    # always loaded
    "data": [
        "security/ir.model.access.csv",
        "views/nursing_note_views.xml",
        "views/resident_views.xml",
        
    ],
    # only loaded in demonstration mode
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 1,
}

