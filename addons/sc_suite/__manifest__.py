{
    'name': 'Serena Care Suite',
    'version': '18.0.1.0.0',
    'category': 'Healthcare',
    'summary': 'Suite completa para gestión de residencias de ancianos',
    'description': """
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
    'author': 'Serena Care Team',
    'website': 'https://www.serena-care.mx',
    'license': 'LGPL-3',
    'depends': [
        # Módulos base de Odoo necesarios
        'base',
        'mail',
        'web',
        
        # Módulos funcionales requeridos
        'calendar',      # Para gestión de actividades y citas
        'project',       # Para planes de cuidados y tareas
        'product',
        'stock',         # Para gestión de medicamentos e inventarios
        'hr',            # Para gestión de cuidadores
        'crm',           # Para gestión de contactos familiares
        
        # Módulos adicionales para funcionalidad completa
        'contacts',      # Gestión avanzada de contactos
        'hr_attendance', # Control de asistencia de cuidadores

        # Módulos de la OCA
        'web_responsive',

        # Módulos específicos de Serena Care
        'sc_base',                # Modelos bases del sistema
        'sc_group',               # Grupos y roles de Serena Care
        'sc_residence',           # Gestión de residencias 
        'sc_sex',                 # Gestión de sexos
        'sc_employee',            # Gestión de empleados
        'sc_resident',            # Gestión de residentes 
        'sc_medication_catalog',  # Gestión del catalogo de medicamento
        'sc_api',                 # API
    ],
    'data': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 1,
}
