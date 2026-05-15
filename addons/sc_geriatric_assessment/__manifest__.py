# -*- coding: utf-8 -*-
{
    'name': "Serena Care - Evaluaciones Geriátricas",

    'summary': "Sistema de registro y seguimiento de evaluaciones geriátricas: Barthel, Lawton-Brody, Norton, FRAIL, GDS-5, SARC-F",

    'description': """
Módulo especializado para el registro, seguimiento y análisis de evaluaciones geriátricas integrales.
        
        Incluye las siguientes escalas validadas:
        - Índice de Barthel (Actividades de la Vida Diaria)
        - Escala de Lawton y Brody (Actividades Instrumentales de la Vida Diaria)
        - Escala de Norton (Riesgo de Úlceras por Presión)
        - Escala FRAIL (Fragilidad)
        - GDS-5 (Escala Geriátrica de Depresión de 5 ítems)
        - SARC-F (Fuerza, Asistencia al caminar, Levantarse de una silla, Subir escaleras, Caídas)
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
        'sc_base',
        'sc_group',
        'sc_resident',
        'sc_employee',
    ],

    # always loaded
    "data": [
        "data/data_scale_dgs5_question.xml",
        "data/data_scale_dgs5_state.xml",
        "data/data_scale_frail_question.xml",
        "data/data_scale_frail_state.xml",
        "data/data_scale_sarcf_state.xml",
        "data/data_scale_sarcf_question_choise.xml",
        "data/data_scale_sarcf_question.xml",
        "data/data_barthel_state.xml",
        "data/data_barthel_question_choise.xml",
        "data/data_barthel_question.xml",
        "data/data_lawton_brody_state.xml",
        "data/data_lawton_brody_question_choise.xml",
        "data/data_lawton_brody_question.xml",
        "security/ir.model.access.csv",
        "views/norton_assessment_views.xml",
        "views/resident_views.xml",
        "views/scalefrail_answer_views.xml",
        "views/scalefrail_assessment_views.xml",
        "views/scalefrail_question_views.xml",
        "views/scalefrail_state_views.xml",
        "views/scalegds5_answer_views.xml",
        "views/scalegds5_assessment_views.xml",
        "views/scalegds5_question_views.xml",
        "views/scalegds5_state_views.xml",
        "views/scalesarcf_answer_views.xml",
        "views/scalesarcf_assessment_views.xml",
        "views/scalesarcf_choise_views.xml",
        "views/scalesarcf_question_views.xml",
        "views/scalesarcf_state_views.xml",
        "views/barthel_answer_views.xml",
        "views/barthel_assessment_views.xml",
        "views/barthel_choise_views.xml",
        "views/barthel_question_views.xml",
        "views/barthel_state_views.xml",
        "views/lawton_brody_answer_views.xml",
        "views/lawton_brody_assessment_views.xml",
        "views/lawton_brody_choise_views.xml",
        "views/lawton_brody_question_views.xml",
        "views/lawton_brody_state_views.xml",
        "views/view_menu.xml"
    ],
    # only loaded in demonstration mode
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 1,
}

