# -*- coding: utf-8 -*-
{
    'name': "Serena Care - Gestión de Signos Vitales",

    'summary': "Registro y seguimiento histórico de signos vitales de los residentes",

    'description': """
Módulo especializado para residencias que permite:
        
• Registrar signos vitales clave (presión arterial, frecuencia cardíaca, saturación de O₂, temperatura, etc.)  
• Historial completo con seguimiento evolutivo  
• Acceso diferenciado para personal  
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
        "data/data_vital_signs.xml",
        "security/ir.model.access.csv",
        "views/vital_signs_views.xml",
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

