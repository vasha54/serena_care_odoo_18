# -*- coding: utf-8 -*-
{
    'name': "Serena Care - Gestión de Catálogo de Medicamentos",

    'summary': """
Módulo para la administración completa de medicamentos, 
incluyendo indicaciones, dosis, formas farmacéuticas y agrupación.
    """,

    'description': """
Sistema especializado para la gestión de medicamentos

        Este módulo permite:
        - Registrar medicamentos con todos sus atributos esenciales
        - Gestionar formas farmacéuticas (comprimidos, jarabes, inyectables, etc.)
        - Administrar grupos terapéuticos de medicamentos
        - Definir indicaciones médicas para cada medicamento
        - Especificar vías de administración y dosis para grupos hetarios
        - Mantener un catálogo organizado con códigos únicos
        - Gestionar composiciones y presentaciones de medicamentos

        Características principales:
        • Catálogo completo de medicamentos
        • Gestión de formas farmacéuticas
        • Administración de grupos terapéuticos
        • Especificación de indicaciones médicas
        • Configuración de dosis y vías de administración
        • Validación de códigos con formato específico
        • Búsqueda avanzada y filtros especializados
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
    'depends': ['base','product'],

    # always loaded
    "data": [
        "security/ir.model.access.csv",
        "data/data_pharmaceutical_form.xml",
        "data/data_product_category_medicament.xml",
        "data/data_product_medicament.xml",
        "views/medicament_category_views.xml",
        "views/medicament_product_views.xml",
        "views/pharmaceutical_form_views.xml",
        "views/route_administration_views.xml",
        "views/views_menu.xml"
    ],
    # only loaded in demonstration mode
    'demo': [],

    'assets': {
        'web.assets_backend': [
            'sc_medication_catalog/static/src/css/form_style.css',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 1,
}

