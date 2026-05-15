# -*- coding: utf-8 -*-
{
    'name': "Serena Care - Evaluaciones del Estado de Ánimo",

    'summary': "Sistema integral para registro y seguimiento de evaluaciones del estado de ánimo en pacientes. Incluye escalas validadas para depresión, ansiedad y bienestar emocional.",

    'description': "Módulo especializado para evaluaciones psicológicas y psiquiátricas del estado de ánimo.",

    'author': 'Serena Care Team',
    'website': 'https://www.serena-care.mx',
    'license': 'LGPL-3',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'version': '18.0.1.0.0',
    'category': 'Healthcare/Mental Health',
    

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'sc_base',
        'sc_group',
        'sc_resident',
        'sc_employee',
],

    # always loaded
    "data": [
        "data/data_mood_state.xml",
        "security/ir.model.access.csv",
        "views/mood_assessment_views.xml",
        "views/mood_state_views.xml",
        "views/resident_views.xml",
        "views/view_menu.xml"
    ],
    # only loaded in demonstration mode
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 1,
}

