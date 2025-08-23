import logging

from odoo import models, fields, api, _, tools
from odoo.exceptions import ValidationError, AccessDenied, UserError
from datetime import timedelta

_logger = logging.getLogger(__name__)


class MedicalIndication(models.Model):
    _inherit = 'medical.indication'

    user_data = fields.Json(
        string="Doctor Datos",
        compute="_compute_user_data",
        store=False,
    )
    resident_data = fields.Json(
        string="Residente Datos",
        compute="_compute_resident_data",
        store=False,
    )
    
    @api.depends('user_id')
    def _compute_user_data(self):
        for record in self:
            record.user_data = record.user_id.read(
                [
                    "id",
                    "name",
                ]
            )[0]
  
    @api.depends('resident_id')
    def _compute_resident_data(self):
        for record in self:
            record.resident_data = record.resident_id.read(
                [
                    "id",
                    "name",
                ]
            )[0]