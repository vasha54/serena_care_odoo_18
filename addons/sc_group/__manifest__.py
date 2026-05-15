# -*- coding: utf-8 -*-
{
    "name": "Serena Care - Roles y Permisos",
    "summary": "Gestión avanzada de roles, permisos y control de accesos",
    "description": """
Módulo avanzado para la gestión de roles y permisos del sistema.
Permite configurar accesos granularmente a vistas, menús y modelos.
        
Características principales:
    - Gestión de roles personalizados
    - Control de acceso a nivel de vistas
    - Permisos por modelo y operación
    - Configuración de visibilidad de menús
    - Herencia de permisos entre roles
    """,
    "author": "Serena Care Team",
    "website": "https://www.serena-care.mx",
    "license": "LGPL-3",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "version": "18.0.1.0.0",
    'category': 'Security',
    'license': 'LGPL-3',
    # any module necessary for this one to work correctly
    "depends": [
        "base",
        "hr",
    ],
    # always loaded
    "data": [
        "security/groups.xml",
        "security/ir.model.access.csv",
        "views/res_groups_views.xml",
        "views/audit_log_views.xml",
        "views/views_menu.xml",
    ],
    # only loaded in demonstration mode
    "demo": [],
    "installable": True,
    "auto_install": False,
    "application": True,
    "sequence": 1,
}
