# -*- coding: utf-8 -*-
{
    "name": "Serena Care - Gestión de Contactos de Proveedores",
    "summary": "Gestión de contactos de proveedores de la red médica de Serena Care",
    "description": """
        Módulo para gestionar los contactos de los proveedores que conforman 
        la red médica de Serena Care, incluyendo reportes personalizados.
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
        "mail",
        "sc_base",
        "sc_group",
    ],
    # always loaded
    "data": [
        "data/data_nomenclature_specialty_supplier.xml",
        "security/ir.model.access.csv",
        "templates/supplier_report.xml",
        "views/nomenclature_specialty_supplier_views.xml",
        "views/supplier_base_views.xml",
        "views/views_menu.xml",
    ],
    # only loaded in demonstration mode
    "demo": [],
    "installable": True,
    "auto_install": False,
    "application": True,
    "sequence": 1,
}
