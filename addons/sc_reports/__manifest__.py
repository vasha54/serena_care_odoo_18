# -*- coding: utf-8 -*-
{
    'name': "Serena Care - Reportes",

    'summary': "Sistema integral de reportes médicos y geriátricos",

    'description': """
Módulo especializado para la gestión y generación de reportes médicos en centros geriátricos

CARACTERÍSTICAS PRINCIPALES:
----------------------------------------
• Reporte de Balance Hídrico - Totales de ingresos, egresos y balance neto
• Reporte de Alimentación - Historial y resumen porcentual por residente
• Reporte de Higiene/Aseo - Registro de eventos y cumplimiento
• Reporte de Estados de Conciencia - Distribución y evolución temporal
• Evaluaciones Neurológicas - Escalas GDS, MOCA, Lawton con interpretación automática
• Reporte de Recreación - Participación en actividades recreativas
• Gestión de Medicamentos - Inventario y alertas de stock
• Plan de Cuidados - Seguimiento de planes activos por residente
• Reporte General del Residente - Consolidado integral de todos los aspectos

FUNCIONALIDADES:
----------------------------------------
• Exportación a PDF y Excel
• Gráficos de tendencias y análisis temporal
• Alertas automáticas por stock bajo de medicamentos
• Interpretación automática de escalas médicas
• Dashboard unificado para acceso rápido a todos los reportes
    """,

    'author': 'Serena Care Team',
    'website': 'https://www.serena-care.mx',
    'license': 'LGPL-3',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'version': '18.0.1.0.0',
    'category': 'Reporting',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'sc_base',
        'sc_group',
        'sc_water_balance',
        'sc_nutrition',
        'sc_medication_inventory',
        'sc_recreational_activity',
        'sc_nursing_notes',
        'sc_medical_notes',
        'sc_mood',
        'sc_neurological_assessment',
        'sc_laboratory_study',
        'sc_geriatric_assessment',
        'sc_vital_signs',
        'sc_water_balance',
        'sc_general_condition_resident',
        'sc_nutrition',
        'sc_hygiene',
    ],

    # always loaded
    "data": [
        "security/ir.model.access.csv",
        "views/wizard/resident_family_report_wizard_view.xml",
        "views/report_dashboard_views.xml",
        "views/resident_views_header.xml",
        "views/resident_views_water_balance.xml",
        "views/resident_views_nutrition.xml",
        "views/resident_views_hygiene.xml",
        "views/resident_views_care_plan.xml",
        "views/resident_views_medication_inventory.xml",
        "views/resident_views_recreational_activity.xml",
        "views/resident_views_geriatric_neurological_assesstement.xml",
        "views/resident_views_family.xml",
        "views/views_menu.xml", 
        "reports/templates/template_header_footer_reports_sc.xml",
        "reports/templates/resident_info_basic.xml",
        "reports/templates/section_general.xml",
        "reports/templates/section_daily_follow.xml",
        "reports/templates/section_indication_medication_inventory.xml",
        "reports/templates/section_clinic_history.xml",
        "reports/templates/section_resident_record_barthel.xml",
        "reports/templates/section_resident_record_frail.xml",
        "reports/templates/section_resident_record_gsd5.xml",
        "reports/templates/section_resident_record_lawton_brondy.xml",
        "reports/templates/section_resident_record_mood.xml",
        "reports/templates/section_resident_record_neurological.xml",
        "reports/templates/section_resident_record_norton.xml",
        "reports/templates/section_resident_record_sarcf.xml",
        "reports/templates/section_resident_family_extra_information.xml",
        "reports/templates/section_resident_family_mood.xml",
        "reports/templates/section_resident_family_nutrition.xml",
        "reports/templates/section_resident_family_recreational_activity.xml",
        "reports/report_resident_full.xml",
        "reports/report_resident_plan_care.xml",
        "reports/report_resident_recreational_activity.xml",
        "reports/report_resident_medication_inventory.xml",
        "reports/report_resident_water_balance.xml",
        "reports/report_resident_nutrition.xml",
        "reports/report_resident_hygiene.xml",
        "reports/report_resident_geriatric_neurological_assessment.xml",
        "reports/report_resident_family.xml",
    ],
    
    "assets": {
        "web.assets_backend": [
            "sc_reports/static/src/css/report_styles.css",
        ],
        "web._assets_primary_variables": [
        ],
    },
    # only loaded in demonstration mode
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 1,
}

