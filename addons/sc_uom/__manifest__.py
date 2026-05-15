# -*- coding: utf-8 -*-
{
    'name': "Serena Care - Unidades de Medida",

    'summary': "Gestión de categorías, unidades de medida y conversiones",

    'description': """
Sistema completo para la gestión de unidades de medida y conversiones.
        
Características principales:
    - Gestión de categorías de unidades de medida
    - Configuración de unidades base y secundarias
    - Sistema de conversión avanzado entre unidades
    - Factores de conversión personalizados
    - Historial de conversiones
    - Integración con productos y categorías
    - Soporte para unidades compuestas
    """,

    "author": "Serena Care Team",
    "website": "https://www.serena-care.mx",
    "license": "LGPL-3",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "version": "18.0.1.0.0",
    'category': 'Inventory',
    'license': 'LGPL-3',
    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'uom',
        'product',
        'sc_base',
        'sc_group',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/data_uom_unit.xml',
        'data/data_uom_time.xml',
        'data/data_uom_medicament.xml',
        'data/data_uom_weight.xml', 
        'data/data_uom_volumen.xml',
        'data/data_uom_length.xml', 
        'views/uom_categories_views.xml',
        'views/uom_units_views.xml',
        'views/view_menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 1,
}

