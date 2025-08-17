# -*- coding: utf-8 -*-
{
    'name': "Serena Care - RESTful API Gateway",

    'summary': """
API Gateway para integraciones seguras con aplicaciones de terceros
| Endpoints RESTful | OAuth2 | Documentación Swagger
    """,

    'description': """
Módulo API Gateway para Serena Care

Transforma Serena Care en una plataforma de integración empresarial con este completo conjunto de herramientas API diseñado para desarrolladores de terceros.

🌐 **Protocolos y Formatos:**
   - RESTful endpoints (JSON)

✨ **Beneficios clave:**
- Conecta Serena - Care con cualquier ecosistema (móvil, web, IoT)
- Reduce tiempo de integración en un 70%
- Mantén el control total sobre datos expuestos

**Casos de uso:**
Apps móviles personalizadas
Integración con sistemas legacy
Soluciones IoT y dispositivos inteligentes

**Endpoints incluidos:**
- /api_serena/v1/login (Autenticación, inicio de sesión)
- /api_serena/v1/logout (Autenticación, cierre de sesión)
- /api_serena/v1/list_residence_login (Residencia, Listar residencias)
- /api_serena/v1/list_residents_this_residence (Residente, Listar residentes de una residencia)
- /api_serena/v1/register_vital_signs (Signos vitales, Crear registro de signos vitales)
    """,

    'author': 'Serena Care Team',
    'website': 'https://www.serena-care.mx',
    'license': 'LGPL-3',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'version': '18.0.1.0.0',
    'category': 'API/Integration',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'sc_group',
        'sc_residence',
        'sc_employee',
        'sc_vital_signs',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 1,
}

