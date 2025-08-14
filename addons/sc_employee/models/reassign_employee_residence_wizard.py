from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class ReassignEmployeeResidenceWizard(models.TransientModel):
    _name = 'reassign.employee.residence.wizard'
    _description = 'Reasignar a los empleados de residencia'
    
    current_residence_id = fields.Many2one(
        'residence_house', 
        string="Residencia/Casa actual",
        default=lambda self: self.env.context.get('active_id')
    )
    new_residence_id = fields.Many2one(
        'residence_house', 
        string="Residencia/Casa destino",
        required=True,
        domain="[('active','=',True),('is_deleted','=',False)]"
    )
    
    def action_reassign_employees(self):
        self.ensure_one()
        
        employees_records = self.env['hr.employee'].search([
            ('residence_id', '=', self.current_residence_id.id)
        ])
        
        for employee in employees_records:
            if employee:
                residences_aviables = employee.alternative_residences_ids.mapped("id") 
                if self.new_residence_id not in residences_aviables:
                    residences_aviables.append(self.new_residence_id.id)
                # Reasignar al nuevo registro A
                employee.write({
                    'alternative_residences_ids': [(6,0,residences_aviables)],
                    'residence_id': self.new_residence_id.id,
                })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': f'Se reasignaron {len(employees_records)} empleados',
                'type': 'success',
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }