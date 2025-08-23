import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class Resident(models.Model):
    _inherit = "resident"

    def open_register_income_wizard(self):
        return {
            "name": f"Nuevo ingreso en la balance hídrico del residente: {self.name}",
            "type": "ir.actions.act_window",
            "res_model": "register.water.balance.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "active_id": self.id,
                "type_annotation": "income",
            },
        }

    def open_register_expense_wizard(self):
        return {
            "name": f"Nuevo egreso en la balance hídrico del residente: {self.name}",
            "type": "ir.actions.act_window",
            "res_model": "register.water.balance.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "active_id": self.id,
                "type_annotation": "expense",
            },
        }

    def action_open_water_balance_report_wizard(self):
        water_balance_data = []
        selection_dict = dict(
            self.env["water.balance.annotation"]._fields["type_annotation"].selection
        )
        for water_balance in self.water_balance_ids:
            type_label = selection_dict.get(water_balance.type_annotation, "")
            water_balance_data.append(
                {
                    "date": water_balance.create_date.strftime("%Y-%m-%d %H:%M")
                    if water_balance.create_date
                    else "",
                    "doctor": water_balance.user_id.name or "",
                    "type": type_label,
                    "notes": water_balance.notes or "Sin detalles",
                    "quality": water_balance.quantity,
                    "route": water_balance.route_id.name or "",
                }
            )

        data = {
            "resident_name": self.name,
            "annotations": water_balance_data,
        }

        # Retornar acción para generar el reporte - FORMA CORRECTA
        return {
            "type": "ir.actions.report",
            "report_name": "sc_water_balance.report_water_balance_template",
            "report_type": "qweb-pdf",
            "data": data,
            "context": self.env.context,
        }
