# -*- coding: utf-8 -*-
{
    "name": "Serena Care - Gestión de Residencias",
    "summary": "Sistema integral para la gestión de residencias y casas de cuidados de ancianos",
    "description": """
Módulo para la gestión completa de residencias y casas de cuidados de ancianos. Incluye gestión 
de los servicios que brindan las residencias y las casas de cuidados.
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
    "depends": [
        "base", 
        "sc_base", 
        "sc_group"
    ],
    # always loaded
    "data": [
        "data/residence_service.xml",
        "data/residence_house.xml",
        "security/ir.model.access.csv",
        "views/residence_house_views.xml",
        "views/residence_service_views.xml",
        "views/view_menu.xml",
    ],
    # only loaded in demonstration mode
    "demo": [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 1,
}
