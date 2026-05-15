# -*- coding: utf-8 -*-
{
    'name': "Serena Care - Gestión de Planes de Cuidado para residentes",

    'summary': """Gestiona planes de cuidado, actividades y objetivos.""",
    'description': """
        Módulo para la Gestión de Planes de Cuidado en Residencias
        ==========================================================

        Este módulo permite a las residencias gestionar de manera integral los planes de cuidado de sus residentes.
        Incluye funcionalidades para:
            * Definir actividades de la vida diaria y niveles de dependencia.
            * Asociar objetivos, acciones, observaciones y resultados a cada actividad.

        Características principales:
            * Configuración flexible de actividades y metas.
            * Interfaz intuitiva y fácil de usar para el personal sanitario.
    """,

    'author': 'Serena Care Team',
    'website': 'https://www.serena-care.mx',
    'license': 'LGPL-3',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'version': '18.0.1.0.0',
    'category': 'Healthcare/Residential Care',

    # any module necessary for this one to work correctly
    'depends': [
        "base",
        "sc_base",
        "sc_group",
        "sc_employee",
        "sc_resident",
    ],

    # always loaded
    "data": [
        "data/data_activity_type.xml",
        "data/data_dependency_level.xml",
        "data/data_care_action.xml",
        "data/data_care_goal.xml",
        "data/data_care_observation.xml",
        "data/data_care_result.xml",
        "data/data_care_level.xml",
        "security/ir.model.access.csv",
        "views/activity_type_views.xml",
        "views/care_action_views.xml",
        "views/care_goal_views.xml",
        "views/care_observation_views.xml",
        "views/care_plan_activity_views.xml",
        "views/care_plan_views.xml",
        "views/care_result_views.xml",
        "views/dependency_level_views.xml",
        "views/care_level_views.xml",
        "views/resident_views.xml",
        "views/view_menu.xml",
        "views/wizard/care_plan_wizard_views.xml"
    ],
    # only loaded in demonstration mode
    'demo': [],
    "installable": True,
    "auto_install": False,
    "application": True,
    "sequence": 1,
}

