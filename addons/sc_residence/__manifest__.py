# -*- coding: utf-8 -*-
{
    "name": "sc_residence",
    "summary": "Short (1 phrase/line) summary of the module's purpose",
    "description": """
Long description of module's purpose
    """,
    "author": "My Company",
    "website": "https://www.yourcompany.com",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "category": "Uncategorized",
    "version": "0.1",
    # any module necessary for this one to work correctly
    "depends": ["base", "sc_base", "sc_group"],
    # always loaded
    "data": [
        "data/residence_service.xml",
        "data/residence_house.xml",
        "security/ir.model.access.csv",
        "views/residence_house_views.xml",
        "views/residence_service_views.xml",
        "views/view_menu.xml",
    ],
    # only loaded in demonstration mode
    "demo": [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 1,
}
