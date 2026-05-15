# -*- coding: utf-8 -*-
{
    "name": "Serena Care - Balance Hídrico",
    "summary": """
 Sistema integral para el control y registro de vías de ingreso/egreso de líquidos en los residentes
    """,
    "description": """
Módulo de Gestión del Balance Hídricos para Residentes

Este módulo proporciona un sistema completo para el control y seguimiento de los ingresos y egresos de líquidos 
en pacientes, ideal para entornos hospitalarios, clínicas y centros de salud.
    """,
    "author": "Serena Care Team",
    "website": "https://www.serena-care.mx",
    "license": "LGPL-3",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "version": "18.0.1.0.0",
    "category": "Healthcare",
    # any module necessary for this one to work correctly
    "depends": [
        "base",
        "sc_base",
        "sc_group",
        "sc_employee",
        "sc_resident",
    ],
    # always loaded
    "data": [
        "data/data_water_balance_route.xml",
        "security/ir.model.access.csv",
        "views/water_balance_annotation_views.xml",
        "views/water_balance_route_views.xml",
        "views/resident_views.xml",
        "views/wizard/register_water_balance_wizard_views.xml",
        "views/wizard/compute_water_balance_range_wizard.xml",
        "views/view_menu.xml",
    ],
    # only loaded in demonstration mode
    "demo": [],
    "installable": True,
    "auto_install": False,
    "application": True,
    "sequence": 1,
}
