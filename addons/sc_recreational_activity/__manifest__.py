# -*- coding: utf-8 -*-
{
    'name': "Serena Care - Gestión de Actividades Recreativas",

    'summary': "Gestión de tipos de actividades y seguimiento para residentes",

    'description': """
Módulo para la gestión de actividades en residencias de cuidados
===============================================================

Este módulo permite:
- Crear y gestionar tipos de actividades personalizadas
- Programar actividades para residentes
- Reportes de actividades realizadas
""",


    'author': 'Serena Care Team',
    'website': 'https://www.serena-care.mx',
    'license': 'LGPL-3',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'version': '18.0.1.0.0',
    'category': 'Healthcare/Residential Care',
    
    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'web',
        'mail',
        'sc_base', 
        'sc_group', 
        'sc_sex', 
        'sc_residence',
        'sc_resident',
    ],

    # always loaded
    "data": [
        "data/data_nomenclature_activity_type.xml",
        "security/ir.model.access.csv",
        "views/wizard/activity_filter_report_wizard_views.xml",
        "views/nomenclature_activity_type_views.xml",
        "views/recreational_activity_views.xml",
        "views/resident_views.xml",
        "views/view_menu.xml",
        "templates/recreational_activity_report.xml"
    ],
    # only loaded in demonstration mode
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 1,
}

