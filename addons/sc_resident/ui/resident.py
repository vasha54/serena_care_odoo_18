import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class Resident(models.Model):
    _inherit  = 'resident'

    show_actions_buttons = fields.Boolean(compute='_compute_show_actions_buttons', store=False)
    

    def _compute_show_actions_buttons(self):
        for record in self:
            record.show_actions_buttons = self.env.context.get('default_readonly', False)

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
            'context': {
                'default_readonly': True,
            }
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