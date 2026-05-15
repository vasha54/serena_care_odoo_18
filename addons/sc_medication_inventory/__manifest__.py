# -*- coding: utf-8 -*-
{
    "name": "Serena Care - Inventario de Medicamentos",
    "summary": "Gestión de inventarios de medicamentos para residentes con control de entradas y salidas",
    "description": """
 Sistema completo para gestionar inventarios de medicamentos de residentes
        ========================================================================

        Este módulo permite:
        - Registrar medicamentos asignados a cada residente
        - Controlar inventarios por residente con cantidades actuales
        - Registrar operaciones de entrada (compras, donaciones, reposiciones)
        - Registrar operaciones de salida (administraciones, pérdidas, vencimientos)
        - Seguimiento completo del stock por residente
        - Alertas de niveles bajos de medicamentos
        - Historial de movimientos de cada medicamento

        Características principales:
        • Gestión por paciente individual
        • Control de lotes y fechas de vencimiento
        • Autorización de familiares para reposiciones
        • Integración con contactos (pacientes y familiares)
        • Sistema de trazabilidad completo
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
    "depends": [
        "base",
        "product",
        "mail",
        "uom",
        "sc_base",
        "sc_group",
        "sc_uom",
        "sc_medication_catalog",
        "sc_resident",
        "sc_medical_indication",
    ],
    # always loaded
    "data": [
        "security/ir.model.access.csv",
        "data/ir_cron.xml",
        "templates/operation_inventory_report.xml",
        "views/medication_inventory_views.xml",
        "views/operation_inventory_views.xml",
        "views/resident_views.xml",
        "views/view_menu.xml",
        "views/wizard/operation_inventory_create_wizard_views.xml",
        "views/wizard/medication_inventory_create_wizard_views.xml"
    ],
    # only loaded in demonstration mode
    "demo": [],
    "installable": True,
    "auto_install": False,
    "application": True,
    "sequence": 1,
}
