# -*- coding: utf-8 -*-
{
    'name': "Serena Care - Notas de Calendario",

    'summary': "Gestionar notas y eventos en el calendario para residentes",

    'description': """
Módulo de Notas de Calendario
        =============================
        Este módulo permite crear y gestionar notas y eventos en el calendario de Odoo, asociados a residentes.
        Características:
        * Crear notas en el calendario con descripción.
        * Gestionar horarios y detalles de eventos.
        * Integrar notas con las vistas de calendario de Odoo.
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
        'calendar',
        'web', 
        'sc_base',
        'sc_group',
        'sc_resident',
        'sc_employee',
        'sc_supplier_contact',
    ],

    # always loaded
    "data": [
        "security/ir.model.access.csv",
        "views/calendar_note_views.xml",
        "views/wizard/create_calendar_note_wizard_views.xml",
        "views/resident_views.xml"
    ],
    "assets": {
        "web.assets_backend": [
            "sc_calendar/static/src/css/calendar_style.css",
        ],
    },
    # only loaded in demonstration mode
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 1,
}

