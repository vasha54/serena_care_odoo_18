from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)

class ResGroups(models.Model):
    _inherit = 'res.groups'

    def action_view_details(self):
        """Abrir vista de formulario en modo solo lectura"""
        self.ensure_one()
        view_id = self.env.ref('sc_group.view_res_groups_form_serena').id
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'current',
            'flags': {'mode': 'readonly'},
            'context': {
                'default_readonly': True,
            }
        }

    def action_edit(self):
        """Abrir vista de formulario en modo edición"""
        self.ensure_one()
        view_id = self.env.ref('sc_group.view_res_groups_form_serena').id
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'current',
        }
