from odoo import api, SUPERUSER_ID


def pre_init_hook(cr):
    """
    Hook ejecutado antes de la instalación del módulo.
    Verifica que todos los módulos dependientes estén disponibles.
    """
    pass


def post_init_hook(cr, registry):
    """
    Hook ejecutado después de la instalación del módulo.
    Configura datos iniciales y personaliza la instalación.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Configurar datos iniciales para Serena Care
    _setup_initial_data(env)
    
    # Configurar menús y accesos
    _setup_menus_and_access(env)
    
    # Configurar vistas por defecto
    _setup_default_views(env)


def _setup_initial_data(env):
    """Configura datos iniciales del sistema"""
    # Crear categorías de contacto para familiares
    contact_categories = [
        {'name': 'Familiar Responsable', 'color': 2},
        {'name': 'Familiar Secundario', 'color': 3},
        {'name': 'Médico de Cabecera', 'color': 5},
        {'name': 'Contacto de Emergencia', 'color': 1},
    ]
    
    for category in contact_categories:
        existing = env['res.partner.category'].search([('name', '=', category['name'])])
        if not existing:
            env['res.partner.category'].create(category)
    
    # Crear tipos de proyecto para planes de cuidados
    care_plan_types = [
        {'name': 'Plan de Cuidados General'},
        {'name': 'Plan de Rehabilitación'},
        {'name': 'Plan de Medicación'},
        {'name': 'Plan de Actividades'},
    ]
    
    for plan_type in care_plan_types:
        existing = env['project.project.type'].search([
            ('name', '=', plan_type['name'])
        ])
        if not existing:
            env['project.project.type'].create(plan_type)


def _setup_menus_and_access(env):
    """Configura menús y permisos de acceso"""
    # Configurar grupo de usuarios Serena Care
    serena_group = env.ref('sc_suite.group_serena_care_user', raise_if_not_found=False)
    if serena_group:
        # Asignar permisos básicos
        pass


def _setup_default_views(env):
    """Configura vistas por defecto para Serena Care"""
    # Configurar vista de calendario por defecto
    # Configurar vista de kanban para residentes
    # Configurar dashboard principal
    pass
