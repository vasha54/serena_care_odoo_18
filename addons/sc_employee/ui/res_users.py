import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied

_logger = logging.getLogger(__name__)

class ResUser(models.Model):
    _inherit = 'res.users'  # Solo hereda de res.users
        
    def action_view_details(self):
        """Abrir vista de formulario en modo solo lectura"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'view_id': False,
            'target': 'current',
            'flags': {'mode': 'readonly'},
        }

    def action_edit(self):
        """Abrir vista de formulario en modo edición"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'view_id': False,
            'target': 'current',
        }

     

    
    