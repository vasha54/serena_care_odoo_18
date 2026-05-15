import logging

from odoo import models, fields, api, _, tools
from odoo.exceptions import ValidationError, AccessDenied, UserError
from datetime import timedelta

_logger = logging.getLogger(__name__)


class VitalSigns(models.Model):
    _inherit = "vital.signs"

    user_data = fields.Json(
        string="Usuaurio Datos",
        compute="_compute_user_data",
        store=False,
    )
    resident_data = fields.Json(
        string="Residente Datos",
        compute="_compute_resident_data",
        store=False,
    )
    
    def _compute_user_data(self):
        for record in self:
            record.user_data = record.user_id.read(
                [
                    "id",
                    "name",
                ]
            )[0]

    def _compute_resident_data(self):
        for record in self:
            record.resident_data = record.resident_id.read(
                [
                    "id",
                    "name",
                ]
            )[0]
