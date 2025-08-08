# -*- coding: utf-8 -*-
{
    'name': "sc_employee",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ["base", "sc_group", "sc_sex", "sc_residence", "hr"],

    # always loaded
    "data": [
        "data/data_department.xml",
        "data/data_job.xml",
        "data/data_res_users.xml",
        "security/ir.model.access.csv",
        "views/employee_views.xml",
        "views/reassign_employee_residence_wizard_views.xml",
        "views/res_users_views.xml",
        "views/residence_house_views.xml",
        "views/views_menu.xml"
    ],
    # only loaded in demonstration mode
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 1,
}

