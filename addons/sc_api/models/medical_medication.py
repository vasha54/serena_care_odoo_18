import logging

from odoo import models, fields, api, _, tools
from odoo.exceptions import ValidationError, AccessDenied, UserError
from datetime import timedelta

_logger = logging.getLogger(__name__)


class MedicalMedication(models.Model):
    _inherit = 'medical.medication'

    medicament_data = fields.Json(
        string="Datos del medicamento",
        compute="_compute_medicament_data",
        store=False,
    )
    
    route_data = fields.Json(
        string="Datos de la vía de administración",
        compute="_compute_route_data",
        store=False,
    )
    dosage_unit_data = fields.Json(
        string="Datos de la unidad de medida de la dosis",
        compute="_compute_dosage_unit_data",
        store=False,
    )
    frequency_unit_data = fields.Json(
        string="Datos de la unidad de medida de la dosis",
        compute="_compute_frequency_unit_data",
        store=False,
    )

    @api.depends('medicament_id')
    def _compute_medicament_data(self):
        for record in self:
            record.medicament_data = record.medicament_id.read(
                [
                    "id",
                    "name",
                ]
            )[0] 

    @api.depends('route_id')
    def _compute_route_data(self):
        for record in self:
            record.route_data = record.route_id.read(
                [
                    "id",
                    "name",
                ]
            )[0]

    @api.depends('dosage_unit')
    def _compute_dosage_unit_data(self):
        for record in self:
            record.dosage_unit_data = record.dosage_unit.read(
                [
                    "id",
                    "name",
                ]
            )[0]

    @api.depends('frequency_unit')
    def _compute_frequency_unit_data(self):
        for record in self:
            if record.frequency_unit:
                record.frequency_unit_data = record.frequency_unit.read(
                    [
                        "id",
                        "name",
                    ]
                )[0]
            else:
                record.frequency_unit_data = False
    