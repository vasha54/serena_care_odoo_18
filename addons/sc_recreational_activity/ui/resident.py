import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class Resident(models.Model):
    _inherit  = 'resident'

    def action_open_activity_recreation_report_pdf_wizard(self):
        self.ensure_one()
        if len(self.activitys_recreations_ids) == 0:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': 'No se puede generar reporte si no existe registros',
                    'type': 'warning',
                    'next': {'type': 'ir.actions.act_window_close'},
                }
            }

        return {
            "name": f"Reporte de actividades recreativas del residente: {self.name}",
            "type": "ir.actions.act_window",
            "res_model": "activity.filter.report.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "active_id": self.id,
                "format_report": "pdf",
            },
        }

    def action_open_activity_recreation_report_excel_wizard(self):
        self.ensure_one()
        if len(self.activitys_recreations_ids) == 0:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': 'No se puede generar reporte si no existe registros',
                    'type': 'warning',
                    'next': {'type': 'ir.actions.act_window_close'},
                }
            }
        
        return {
            "name": f"Reporte de actividades recreativas del residente: {self.name}",
            "type": "ir.actions.act_window",
            "res_model": "activity.filter.report.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "active_id": self.id,
                "format_report": "excel",
            },
        }

