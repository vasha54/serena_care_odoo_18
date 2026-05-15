# -*- coding: utf-8 -*-
{
    'name': "Serena Care - Estudios de Laboratorio",

    'summary': "Gestión y almacenamiento de estudios de laboratorio de residentes",

    'description': """
Gestión de Estudios de Laboratorio
=================================

Este módulo permite:
- Registrar estudios de laboratorio asociados a pacientes/residentes
- Subir y almacenar archivos (PDF, JPG, PNG)
- Previsualizar estudios directamente desde el formulario
- Controlar quién registra cada estudio
- Mantener trazabilidad clínica de los resultados
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
        'web',
        'sc_group',
        'sc_base',
        'sc_resident'
    ],

    # always loaded
    "data": [
        "security/ir.model.access.csv",
        "views/laboratory_file_views.xml",
        "views/resident_views.xml",
        "views/views_menu.xml",
        
    ],
    "assets": {
        "web.assets_backend": [
            "sc_laboratory_study/static/src/css/laboratory_study.css",
        ]
    },
    # only loaded in demonstration mode
    'demo': [],
    "installable": True,
    "auto_install": False,
    "application": True,
    "sequence": 1,
    
}

