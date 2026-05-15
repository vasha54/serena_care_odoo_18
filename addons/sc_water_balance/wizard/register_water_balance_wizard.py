import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class RegisterWaterBalanceWizard(models.TransientModel):
    _name = "register.water.balance.wizard"
    _description = "Wizard para registrar ingreso/egreso del balance Hídrico"

    resident_id = fields.Many2one(
        "resident",
        string="Residente",
        required=True,
        ondelete="restrict",
        default=lambda self: self.env.context.get("active_id"),
    )
    user_id = fields.Many2one(
        "res.users",
        string="Registrado por",
        default=lambda self: self.env.user,
        required=True,
        ondelete="restrict",
    )
    route_id = fields.Many2one(
        "water.balance.route",
        string="Vía de Ingreso/Egreso",
        required=True,
        ondelete="restrict",
    )
    type_annotation = fields.Selection(
        [("income", "Ingreso"), ("expense", "Egreso")],
        string="Tipo",
        required=True,
        default=lambda self: self.env.context.get("type_annotation"),
    )
    quantity = fields.Float(string="Cantidad (ml)", digits=(3, 1), required=True)
    notes = fields.Text(string="Observaciones")
    date = fields.Datetime(
        string='Fecha/Hora', 
        default=fields.Datetime.now,
        required=True
    )

    def action_register_annotation(self):
        self.ensure_one()
        WaterBalanceAnnotation = self.env["water.balance.annotation"].sudo()
        WaterBalanceAnnotation.create(
            {
                "user_id": self.user_id.id,
                "resident_id": self.resident_id.id,
                "route_id": self.route_id.id,
                "type_annotation": self.type_annotation,
                "quantity": self.quantity,
                "notes": self.notes,
                "date": self.date,
            }
        )
