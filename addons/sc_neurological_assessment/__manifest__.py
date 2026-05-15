# -*- coding: utf-8 -*-
{
    'name': "Serena Care - Evaluaciones Neurológicas",

    'summary': "Permite registrar las evaluaciones neurológicas realizadas a los residentes",

    'description': """
Módulo para gestionar el registro de pruebas neurológicas en residentes.
        Permite:
        - Registrar pruebas realizadas a pacientes, con fecha, profesional responsable, resultados y observaciones.
        - Visualizar el historial de pruebas por paciente.
        
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
        "data/data_neurological_state.xml",
        "security/ir.model.access.csv",
        "views/neurological_assessment_views.xml",
        "views/neurological_state_views.xml",
        "views/resident_views.xml",
        "views/view_menu.xml",
    ],
    # only loaded in demonstration mode
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 1,
}

