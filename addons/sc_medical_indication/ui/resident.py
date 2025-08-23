import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class Resident(models.Model):
    _inherit  = 'resident'

    def open_register_medical_indication_wizard(self):
        return {
            'name': f"Nueva indicación médica general: {self.name}",
            'type': 'ir.actions.act_window',
            'res_model': 'register.medical.indication.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_current_resident_id': self.id,
            }
        }

    def open_register_medical_medication_wizard(self):
        return {
            'name': f"Nueva indicación médica de medicamento: {self.name}",
            'type': 'ir.actions.act_window',
            'res_model': 'register.medical.medication.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_current_resident_id': self.id,
            }
        }

    def action_open_medical_indication_report_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Generar Reporte de Indicaciones Médicas',
            'res_model': 'medical.indication.report.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_id': self.id},
        }
    
    