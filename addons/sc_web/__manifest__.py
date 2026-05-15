# -*- coding: utf-8 -*-
{
    'name': "Serena Care - Componentes Visuales Genéricos",

    'summary': "Proporciona componentes gráficos y visuales reutilizables para vistas de Odoo",

    'description': """
Módulo que ofrece una colección de componentes visuales genéricos (widgets, plantillas, estilos, etc.)
        que pueden ser utilizados en diferentes vistas de otros módulos.

        Características:
        - Widgets personalizados para kanban, listas, formularios.
        - Estilos CSS reutilizables y temas visuales.
        - Plantillas QWeb para componentes UI comunes (tarjetas, gráficos simples, etc.).
        - Funcionalidades JavaScript para mejorar la interacción del usuario.
        - Integración con el framework web de Odoo.

        Este módulo no añade funcionalidad de negocio por sí mismo, sino que sirve como base
        para que otros módulos puedan extender la interfaz de usuario de manera consistente.
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'web'
    ],
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
    ],
    'assets': {
        'web.assets_backend': [
            'sc_web/static/src/js/bool_badge_field_widget.js',
            'sc_web/static/src/xml/bool_badge_field_widget.xml',
        ],
    },
    # only loaded in demonstration mode
    'demo': [],
    "installable": True,
    "auto_install": False,
    "application": True,
    "sequence": 1,
}

