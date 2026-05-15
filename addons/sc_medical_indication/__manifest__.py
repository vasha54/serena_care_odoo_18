# -*- coding: utf-8 -*-
{
    'name': "Serena Care - Indicaciones Médicas",

    'summary': "Gestión de indicaciones médicas y generales para residentes de casas de cuidado",

    'description': """
 Módulo para la gestión integral de indicaciones médicas y generales de residentes en casas de 
 cuidado y residencias geriátricas.
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
        'product',
        'sc_base',
        'sc_group',
        'sc_uom',
        'sc_resident',
        'sc_employee',
        'sc_medication_catalog',
    ],

    # always loaded
    "data": [
        "security/ir.model.access.csv",
        "views/medical_indication_views.xml",
        "views/medical_medication_views.xml",
        "views/resident_views.xml",
        "views/unified_medical_indication_views.xml",
        "views/view_menu.xml",
        "views/wizard/register_medical_indication_wizard_views.xml",
        "views/wizard/register_medical_medication_wizard_views.xml",
        "views/wizard/medical_indication_report_wizard_views.xml",
        "templates/medical_indication_report_template.xml",
    ],
    # only loaded in demonstration mode
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 1,
}

