import logging
import base64
import os

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class ResidentFamily(models.Model):
    _inherit = 'resident.family'

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

    def action_upload_avatar(self):
        """Abrir vista de formulario en modo edición"""
        self.ensure_one()
        return {
            'name': f"Cambiar la imagen del familiar: {self.name}",
            'type': 'ir.actions.act_window',
            'res_model': 'change.photo.family.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_current_family_id': self.id,
            }
        }

    def action_view_history(self):
        """Abrir vista de formulario con el historial de cambios de edición"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'view_id': self.env.ref('sc_resident.view_resident_family_form_history_edit').id,
            'target': 'current',
            'flags': {'mode': 'readonly'},
        }