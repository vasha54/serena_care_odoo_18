import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class CarePlanWizardLine(models.TransientModel):
    _name = 'care.plan.wizard.line'
    _description = 'Línea de Actividad para el Asistente de Plan de Cuidado'

    wizard_id = fields.Many2one(
        'care.plan.wizard', 
        string="Asistente", 
        required=True,
        ondelete='cascade'  # Si se borra el wizard, se borran sus líneas
    )
    
    # Campos para la actividad
    activity_id = fields.Many2one(
        'activity.type', 
        string="Actividad", 
        required=True
    )
    dependency_level_id = fields.Many2one(
        'dependency.level', 
        string="Nivel de Dependencia", 
        required=True
    )
    
    # Relaciones Many2many (seleccionables por el usuario)
    goal_ids = fields.Many2many('care.goal', string="Objetivos",required=True)
    action_ids = fields.Many2many('care.action', string="Acciones",required=True)
    observation_ids = fields.Many2many('care.observation', string="Observaciones",required=True)
    result_ids = fields.Many2many('care.result', string="Resultados",required=True)


class CarePlanWizard(models.TransientModel):
    _name = 'care.plan.wizard'
    _description = 'Asistente para Crear Plan de Cuidado'
    
    resident_id = fields.Many2one('resident', string="Residente", required=True)
    diagnosis = fields.Text(
        string='Diagnóstico',
    )
    care_level_id = fields.Many2one(
        'care.level',
        string="Nivel de Cuidado",
        required=True,
        domain=[('active','=',True)]
    )
    # Líneas de actividades para el plan
    activity_line_ids = fields.One2many(
        'care.plan.wizard.line', 
        'wizard_id', 
        string="Actividades del Plan"
    )
    
    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        # Si se pasa el residente por contexto (desde un botón en residente)
        if self._context.get('active_model') == 'resident' and self._context.get('active_id'):
            res['resident_id'] = self._context['active_id']
        return res
    
    def action_create_care_plan(self):
        # Crear el plan de cuidado
        care_plan = self.env['care.plan'].create({
            'resident_id': self.resident_id.id,
            'care_level_id':self.care_level_id.id,
            'diagnosis':self.diagnosis,
        })
        
        # Crear las actividades del plan
        for line in self.activity_line_ids:
            self.env['care.plan.activity'].create({
                'care_plan_id': care_plan.id,
                'activity_id': line.activity_id.id,
                'dependency_level_id': line.dependency_level_id.id,
                'goal_ids': [(6, 0, line.goal_ids.ids)],
                'action_ids': [(6, 0, line.action_ids.ids)],
                'observation_ids': [(6, 0, line.observation_ids.ids)],
                'result_ids': [(6, 0, line.result_ids.ids)],
            })

        self.resident_id.write({'care_plan_id': care_plan.id})
        
        


