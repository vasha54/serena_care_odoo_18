import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class Resident(models.Model):
    _inherit  = 'resident'

    def open_register_care_plan_wizard(self):
        self.ensure_one()
        return {
            'name': f"Crear plan de cuidado del residente: {self.name}",
            'type': 'ir.actions.act_window',
            'res_model': 'care.plan.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_resident_id': self.id,
            }
        }

    
    
    