from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class ReassignResidentResidenceWizard(models.TransientModel):
    _name = 'reassign.resident.residence.wizard'
    _description = 'Reasignar a los residentes de residencia'
    
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
    
    def action_reassign_residents(self):
        self.ensure_one()
        
        residents_records = self.env['resident'].search([
            ('residence_id', '=', self.current_residence_id.id)
        ])
        
        residents_records.write({
                    'residence_id': self.new_residence_id.id,
                })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': f'Se reasignaron {len(residents_records)} residentes',
                'type': 'success',
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }