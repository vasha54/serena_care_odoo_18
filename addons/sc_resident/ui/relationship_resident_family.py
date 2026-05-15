import logging
import base64
import os

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class RelationshipResidentFamily(models.Model):
    _inherit = 'relationship.resident.family'

    def action_view_details(self):
        """Abrir vista de formulario en modo solo lectura"""
        self.ensure_one()
        return {
            'name': f"Detalles del familiar: {self.family_name}",
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'view_id': False,
            'target': 'new',
            'flags': {'mode': 'readonly'},
        }

    