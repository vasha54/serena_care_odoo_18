import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class Resident(models.Model):
    _inherit  = 'resident'

    def open_register_new_family_for_resident_wizard(self):
        return {
            'name': f"Nuevo familiar del residente: {self.name}",
            'type': 'ir.actions.act_window',
            'res_model': 'register.new.family.resident.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_current_resident_id': self.id,
            }
        }
    
    def open_search_new_family_for_resident_wizard(self):
        return {
            'name': f"Buscar familiar del residente: {self.name}",
            'type': 'ir.actions.act_window',
            'res_model': 'search.new.family.resident.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_current_resident_id': self.id,
            }
        }
