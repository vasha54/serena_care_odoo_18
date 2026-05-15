import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class Resident(models.Model):
    _inherit = "resident"

    def open_register_income_wizard(self):
        return {
            "name": f"Nuevo ingreso en balance hídrico del residente: {self.name}",
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
            "name": f"Nuevo egreso en balance hídrico del residente: {self.name}",
            "type": "ir.actions.act_window",
            "res_model": "register.water.balance.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "active_id": self.id,
                "type_annotation": "expense",
            },
        }

    def open_compute_water_balance_range_wizard(self):
        return {
            "name": f"Calcular balance hídrico del residente: {self.name}",
            "type": "ir.actions.act_window",
            "res_model": "compute.water.balance.range.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "active_id": self.id,
            },
        }

    
