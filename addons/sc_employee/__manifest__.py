# -*- coding: utf-8 -*-
{
    'name': "Serena Care - Empleados",

    'summary': """
    Gestión completa de empleados y usuarios para residencias Serena Care.
    Incluye creación, modificación, eliminación.
    """,

    'description': """
    Módulo integral para la gestión de recursos humanos en residencias Serena Care.
        
        Características principales:
        - Gestión completa de empleados (alta, baja, modificación)
        - Creación automática de usuarios asociados a empleados
        - Sistema de roles y permisos personalizados para Serena Care
        - Gestión de contraseñas con seguridad mejorada
        - Soft delete para usuarios y empleados
        - Interfaz personalizada para administradores
        
        Grupos de seguridad incluidos:
        - Administración (Dirección, Gerentes)
        - Gerente Salud (Médicos)
        - Enfermería (Cuidadores)
    """,

    'author': 'Serena Care Team',
    'website': 'https://www.serena-care.mx',
    'license': 'LGPL-3',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'version': '18.0.1.0.0',
    'category': 'Human Resources',

    # any module necessary for this one to work correctly
    'depends': ["base", "sc_group", "sc_sex", "sc_residence", "hr"],

    # always loaded
    "data": [
        "data/data_department.xml",
        "data/data_job.xml",
        # "data/data_res_users.xml",
        "security/ir.model.access.csv",
        "views/hr_employee_certificate_views.xml",
        "views/hr_employee_views.xml",
        "views/reassign_employee_residence_wizard_views.xml",
        "views/res_users_views.xml",
        "views/residence_house_views.xml",
        "views/views_menu.xml",
        "views/wizard/change_photo_employee_wizard_views.xml",
        "views/wizard/res_user_select_residences_wizard_views.xml",
    ],
    # only loaded in demonstration mode
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 1,
}

