{
    "name": "Serena Care Suite",
    "version": "18.0.1.0.0",
    "category": "Healthcare",
    "summary": "Suite completa para gestión de residencias de ancianos",
    "description": """
Serena Care Suite
=================

Suite completa para la automatización y gestión de residencias de ancianos en México.

Este módulo instala todos los componentes necesarios para:

* Gestión de residentes y cuidadores
* Monitorización de salud (signos vitales, estado de ánimo, dolor)
* Gestión de medicamentos e inventarios
* Planes de cuidados y actividades
* Evaluaciones y escalas de riesgo
* Comunicación y registros
* Dashboard e informes

Funcionalidades principales:
---------------------------
* **Gestión de Usuarios**: Sistema de autenticación para cuidadores
* **Gestión de Residentes**: Perfiles detallados con información médica
* **Monitorización de Salud**: Registro de signos vitales, estado emocional y dolor
* **Medicamentos**: Control de administración y planes de medicación
* **Actividades**: Calendario y seguimiento de participación
* **Evaluaciones**: Escalas estandarizadas (Norton, Barthel, etc.)
* **Comunicación**: Notas, incidencias y contactos de emergencia
* **Informes**: Dashboard ejecutivo y reportes detallados

Módulos incluidos:
-----------------
* Calendar - Gestión de actividades y citas médicas
* Project - Planes de cuidados y tareas asignadas
* Stock - Inventario de medicamentos y suministros
* HR - Gestión de personal cuidador
* CRM - Contactos familiares y médicos de emergencia

Desarrollado específicamente para cumplir con las necesidades de 
residencias de ancianos en México.
    """,
    "author": "Serena Care Team",
    "website": "https://www.serena-care.mx",
    "license": "LGPL-3",
    "depends": [
        # Módulos base de Odoo necesarios
        "base",
        "mail",
        "web",
        # Módulos funcionales requeridos
        # Módulos adicionales para funcionalidad completa
        # Módulos de la OCA
        "web_responsive",
        # Módulos específicos de Serena Care
        "sc_base",  # Modelos bases del sistema
        "sc_group",  # Grupos y roles de Serena Care
        "sc_sex",  # Gestión de sexos
        "sc_uom",  # Gestión de las unidades de medición y sus categorias
        "sc_residence",  # Gestión de residencias
        "sc_employee",  # Gestión de empleados
        "sc_resident",  # Gestión de residentes
        "sc_medication_catalog",  # Gestión del catalogo de medicamento
        "sc_vital_signs",  # Gestión de los signos vitales de los residentes
        "sc_medical_indication",  # Gestión de las indicaciones médicas de los residentes
        "sc_water_balance",  # Gestión del balance híbrico
        "sc_supplier_contact",  # Gestión de los contactos de los proveedores que
        # que conforman la red médica
        "sc_medication_inventory",  # Getión del inventario de medicamento
        "sc_recreational_activity",  # Gestión de las actividades recreativas
        "sc_care_plan",  # Gestión del plan de cuidados
        "sc_calendar",  # Gestión de notas en el calendario
        "sc_nursing_notes",  # Gestión de notas de enfemerías
        "sc_medical_notes",  # Gestión de notas médicas
        "sc_anomalies",  # Gestión de anomalías
        "sc_nutrition",  # Gestión de alimentos
        "sc_mood",  # Gestión del ánimo
        "sc_hygiene",  # Gestión de la higiene
        "sc_neurological_assessment",  # Gestión de las evaluaciones neurológicas
        "sc_pain_scale",  # Gestión del dolor
        "sc_geriatric_assessment",  # Gestión de las evaluaciones geríatrías
        "sc_general_condition_resident", #Gestión de las comprobaciones del estado de los residentes
        "sc_laboratory_study", #Gestión de los estudios de los laboratorios de los residentes
        "sc_reports",  # Reportes
        "sc_api",  # API
    ],
    "data": [
        "security/rules.xml",
        "data/resource_data.xml",
        "data/system_parameter_data.xml",
        # "data/palette_data.xml",
        "views/views_dashboard.xml",
        "views/views_login.xml",
        "views/menu_icons.xml",
    ],
          
    "assets": {
        "web.assets_backend": [
            "sc_suite/static/src/scss/primary_variables.scss",
            "sc_suite/static/src/css/themes/verde-degradado.css",
            "sc_suite/static/src/css/dashboard.css",
            "sc_suite/static/lib/chart.js/chart.umd.min.js",
            "sc_suite/static/src/js/card_info_residents.js",
            "sc_suite/static/src/js/card_info_average_age.js",
            "sc_suite/static/src/js/pie_chart_distribution_age.js",
            "sc_suite/static/src/js/medical_appointment_today.js",
            "sc_suite/static/src/js/doughnut_chart_health_status.js",
            "sc_suite/static/src/js/card_info_time_residence.js",
            "sc_suite/static/src/js/card_info_sex_distribution.js",
            "sc_suite/static/src/js/card_filter_residence.js",
            "sc_suite/static/src/js/bar_chart_week_appointments.js",
            "sc_suite/static/src/js/dashboard.js",
            "sc_suite/static/src/js/favicon.js",
            "sc_suite/static/src/xml/card_info_residents.xml",
            "sc_suite/static/src/xml/card_info_average_age.xml",
            "sc_suite/static/src/xml/bar_chart_week_appointments.xml",
            "sc_suite/static/src/xml/card_filter_residence.xml",
            "sc_suite/static/src/xml/card_info_sex_distribution.xml",
            "sc_suite/static/src/xml/card_info_time_residence.xml",
            "sc_suite/static/src/xml/doughnut_chart_health_status.xml",
            "sc_suite/static/src/xml/medical_appointment_today.xml",
            "sc_suite/static/src/xml/pie_chart_distribution_age.xml",
            "sc_suite/static/src/xml/dashboard.xml",
        ],
        "web._assets_primary_variables": [
            "sc_suite/static/src/scss/primary_variables.scss",
        ],
    },
    "installable": True,
    "auto_install": False,
    "application": True,
    "sequence": 1,
}
