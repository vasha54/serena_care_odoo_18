import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class Resident(models.Model):
    _inherit  = 'resident'
    
    def action_upload_laboraty_study(self):
        self.ensure_one()
        return {
            'name': f"Subir estudio de laboratorio del residente: {self.name}",
            'type': 'ir.actions.act_window',
            'res_model': 'laboratory.file',
            'res_id': False,
            'view_mode': 'form',
            'view_id': self.env.ref('sc_laboratory_study.view_laboratory_file_form_wizard').id,
            'target': 'new',
            'context': {
                'default_current_resident_id': self.id,
            }
        }