import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)

class CarePlan(models.Model):
    _name = 'care.plan'
    _description = 'Plan de Cuidado'

    resident_id = fields.Many2one('resident', string="Residente", required=True)
    residence_id =  fields.Many2one(
        string="Residencia",
        related='resident_id.residence_id', 
        readonly=True
    )
    diagnosis = fields.Text(
        string='Diagnóstico',
    )
    care_level_id = fields.Many2one(
        'care.level',
        string="Nivel de Cuidado",
        required=True,
        domain=[('active','=',True)]
    )

    plan_activity_ids = fields.One2many('care.plan.activity', 'care_plan_id', string="Actividades del Plan")
    count_activitys = fields.Integer(compute='_compute_fields', string='Actividades')
    count_dependency_level = fields.Integer(compute='_compute_fields', string='Nivel de Dependencia')
    count_goals = fields.Integer(compute='_compute_fields', string='Objetivos')
    count_actions = fields.Integer(compute='_compute_fields', string='Acciones')
    count_observations = fields.Integer(compute='_compute_fields', string='Observaciones')  
    count_results = fields.Integer(compute='_compute_fields', string='Resultados')  

    @api.depends('plan_activity_ids')
    def _compute_fields(self):
        for r in self:
            r.count_activitys = 0
            r.count_dependency_level = 0
            r.count_goals = 0
            r.count_actions = 0
            r.count_observations = 0
            r.count_results = 0
            if r.plan_activity_ids:
                r.count_activitys = len(r.plan_activity_ids)
                r.count_dependency_level = len(r.plan_activity_ids)
                for act in r.plan_activity_ids:
                    r.count_goals = r.count_goals + len(act.goal_ids)
                    r.count_actions = r.count_actions + len(act.action_ids)
                    r.count_observations = r.count_observations + len(act.observation_ids)
                    r.count_results = r.count_results + len(act.result_ids)
    

    @api.depends('resident_id')
    def _compute_display_name(self):
        for r in self:
            r.display_name = f"Plan de cuidados del residente {r.resident_id.name} de la residencia {r.residence_id.name}"
            
    @api.model
    def create(self, values):
        records = super().create(values)
        # Crear log de auditoría para cada registro creado
        for record in records:
            self.env['audit.log'].sudo().crud_audit_log(record, 'care.plan', 'create')
        return records

    def write(self, values):
        # Guardar estado anterior para detectar cambios (opcional, mejora la calidad del detalle)
        old_values = {}
        for record in self:
            old_values[record.id] = {
                field: record[field] for field in values if field in record._fields and not record._fields[field].compute
            }
        result = super().write(values)
        # Después de la escritura, crear logs con los campos modificados
        for record in self:
            changed_fields = []
            for field, new_val in values.items():
                if field in old_values.get(record.id, {}):
                    old_val = old_values[record.id][field]
                    if old_val != record[field]:
                        changed_fields.append(f"{field}: {old_val!r} -> {record[field]!r}")
                else:
                    # Campo no almacenado o no presente en el registro anterior, se registra igual
                    changed_fields.append(f"{field}: {record[field]!r}")
            if changed_fields:
                details = "Campos modificados: " + "; ".join(changed_fields)
            else:
                details = "Modificación sin cambios detectados"
            self.env['audit.log'].sudo().crud_audit_log(record, 'care.plan', 'write', extra_details=details)
        return result

    def unlink(self):
        # Antes de eliminar, crear logs para cada registro
        for record in self:
            self.env['audit.log'].sudo().crud_audit_log(record, 'care.plan', 'unlink')
        return super().unlink()

class CarePlanActivity(models.Model):
    _name = 'care.plan.activity'
    _description = 'Actividad del Plan de Cuidado'
    
    care_plan_id = fields.Many2one('care.plan', string="Plan de Cuidado", required=True)
    dependency_level_id = fields.Many2one(
        'dependency.level', 
        string="Nivel de Dependencia", 
        required=True,
        domain=[('active','=',True)]
    )
    activity_id = fields.Many2one(
        'activity.type', 
        string="Actividad", 
        required=True,
        domain=[('active','=',True)]
    )
    
    # Relaciones Many2many con los modelos independientes
    goal_ids = fields.Many2many(
        'care.goal', 
        string="Objetivos",
        domain=[('active','=',True)]
    )
    action_ids = fields.Many2many(
        'care.action', 
        string="Acciones",
        domain=[('active','=',True)]
    )
    observation_ids = fields.Many2many(
        'care.observation', 
        string="Observaciones",
        domain=[('active','=',True)]
    )
    result_ids = fields.Many2many(
        'care.result', 
        string="Resultados",
        domain=[('active','=',True)]
    )

    filtered_goal_ids = fields.Many2many(
        'care.goal', 
        string="Filtered Goals",
        compute='_compute_filtered_ids'  # This computes the available goals
    )
    filtered_action_ids = fields.Many2many(
        'care.action', 
        string="Filtered Actions",
        compute='_compute_filtered_ids'  # This computes the available actions
    )
    filtered_result_ids = fields.Many2many(
        'care.result', 
        string="Filtered Results",
        compute='_compute_filtered_ids'  # This computes the available results
    )
    filtered_observation_ids = fields.Many2many(
        'care.observation', 
        string="Filtered Observations",
        compute='_compute_filtered_ids'  # This computes the available observations
    )

    _sql_constraints = [
        ('activity_dependency_unique', 'unique(care_plan_id ,activity_id)', 
         'La combinación Plan Cuidado-Actividaddebe ser única.'),
    ]

    # Compute method for the new field
    @api.depends('activity_id','dependency_level_id')
    def _compute_filtered_ids(self):
        for record in self:
            if record.activity_id and record.dependency_level_id:
                # Search for goals where activity_type_ids contains the current activity_id
                record.filtered_goal_ids = self.env['care.goal'].search([
                    ('activity_type_ids', 'in', record.activity_id.id),
                    ('dependency_level_ids','in',record.dependency_level_id.id),
                    ('active','=',True),
                ])
                record.filtered_action_ids = self.env['care.action'].search([
                    ('activity_type_ids', 'in', record.activity_id.id),
                    ('dependency_level_ids','in',record.dependency_level_id.id),
                    ('active','=',True),
                ])
                record.filtered_result_ids = self.env['care.result'].search([
                    ('activity_type_ids', 'in', record.activity_id.id),
                    ('dependency_level_ids','in',record.dependency_level_id.id),
                    ('active','=',True),
                ]) 
                record.filtered_observation_ids = self.env['care.observation'].search([
                    ('activity_type_ids', 'in', record.activity_id.id),
                    ('dependency_level_ids','in',record.dependency_level_id.id),
                    ('active','=',True),
                ]) 
            else:
                record.filtered_goal_ids = False
                record.filtered_action_ids = False
                record.filtered_result_ids = False
                record.filtered_observation_ids = False

    @api.model
    def default_get(self, fields_list):
        # Obtener los valores por defecto del método original
        defaults = super(CarePlanActivity, self).default_get(fields_list)
        # Si el contexto trae un 'default_care_plan_id', usarlo
        if self._context.get('default_care_plan_id'):
            defaults['care_plan_id'] = self._context['default_care_plan_id']
        return defaults

    @api.constrains('care_plan_id', 'activity_id')
    def _check_unique_activity_per_plan(self):
        for record in self:
            # Buscar si ya existe un registro con la misma combinación
            existing_activity = self.search([
                ('care_plan_id', '=', record.care_plan_id.id),
                ('activity_id', '=', record.activity_id.id),
                ('id', '!=', record.id)  # Excluir el registro actual en una actualización
            ], limit=1)
            if existing_activity:
                raise ValidationError("La combinación Plan de Cuidado y Actividad debe ser única.")   
            
    @api.model
    def create(self, values):
        records = super().create(values)
        # Crear log de auditoría para cada registro creado
        for record in records:
            self.env['audit.log'].sudo().crud_audit_log(record, 'care.plan.activity', 'create')
        return records

    def write(self, values):
        # Guardar estado anterior para detectar cambios (opcional, mejora la calidad del detalle)
        old_values = {}
        for record in self:
            old_values[record.id] = {
                field: record[field] for field in values if field in record._fields and not record._fields[field].compute
            }
        result = super().write(values)
        # Después de la escritura, crear logs con los campos modificados
        for record in self:
            changed_fields = []
            for field, new_val in values.items():
                if field in old_values.get(record.id, {}):
                    old_val = old_values[record.id][field]
                    if old_val != record[field]:
                        changed_fields.append(f"{field}: {old_val!r} -> {record[field]!r}")
                else:
                    # Campo no almacenado o no presente en el registro anterior, se registra igual
                    changed_fields.append(f"{field}: {record[field]!r}")
            if changed_fields:
                details = "Campos modificados: " + "; ".join(changed_fields)
            else:
                details = "Modificación sin cambios detectados"
            self.env['audit.log'].sudo().crud_audit_log(record, 'care.plan.activity', 'write', extra_details=details)
        return result

    def unlink(self):
        # Antes de eliminar, crear logs para cada registro
        for record in self:
            self.env['audit.log'].sudo().crud_audit_log(record, 'care.plan.activity', 'unlink')
        return super().unlink()     


    
    
