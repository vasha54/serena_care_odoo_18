# -*- coding: utf-8 -*-
{
    'name': "Serena Care - Condición General del Residente",

    'summary': "Calcula automáticamente el estado de los residentes basado en reglas de especialistas",

    'description': """
Módulo que permite definir reglas por especialistas para calcular el estado de los pacientes
de forma automática y periódica, utilizando los resultados de pruebas específicas.
        
        Características principales:
        - Cálculo automático del estado de pacientes mediante un cron programado.
        - Historial de estados de pacientes.
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
        'sc_group',
        'sc_base',
        'sc_resident',
        'sc_vital_signs',
        'sc_anomalies',
        'sc_neurological_assessment',
        'sc_pain_scale',
        ],

    # always loaded
    "data": [
        "data/ir_cron.xml",
        "security/ir.model.access.csv",
        "views/medical_resident_state_views.xml",
        "views/resident_views.xml",
        "views/view_menu.xml",
    ],
    # only loaded in demonstration mode
    'demo': [],
    "installable": True,
    "auto_install": False,
    "application": True,
    "sequence": 1,
}

