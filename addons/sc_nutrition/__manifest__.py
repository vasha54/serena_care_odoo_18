# -*- coding: utf-8 -*-
{
    'name': "Serena Care - Gestión de Alimentación",

    'summary': "Sistema de gestión de niveles de alimentación y alimentación para residentes de casas de cuidado",

    'description': """
Módulo para la gestión completa de alimentación los residentes de casas de cuidado.
        
        Características principales:
        * Configuración de niveles de alimentación de los residente
        * Registro y seguimiento de la alimentación por residente
    """,

    'author': 'Serena Care Team',
    'website': 'https://www.serena-care.mx',
    'license': 'LGPL-3',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'version': '18.0.1.0.0',
    'category': 'Healthcare',

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
        "data/data_nutrition_level.xml",
        "security/ir.model.access.csv",
        "views/nutrition_level_views.xml",
        "views/nutrition_views.xml",
        "views/resident_views.xml",
        "views/view_menu.xml"
    ],
    # only loaded in demonstration mode
    'demo': [],
    "installable": True,
    "auto_install": False,
    "application": True,
    "sequence": 1,
}

