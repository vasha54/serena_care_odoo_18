import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)

class CarePlan(models.Model):
    _inherit = 'care.plan'
    
    care_level = fields.Json(
        string="Nivel de cuidado",
        compute="_compute_care_level_data",
        store=False,
    )
    plan_activity = fields.Json(
        string="Activdades",
        compute="_compute_plan_activity_data",
        store=False,
    )
    resident = fields.Json(
        string="Residente Datos",
        compute="_compute_resident_data",
        store=False,
    )
    
    def _compute_care_level_data(self):
        for record in self:
            record.care_level = record.care_level_id.read(
                [
                    "id",
                    "name",
                ]
            )[0]

    def _compute_plan_activity_data(self):
        for record in self:
            record.plan_activity = record.plan_activity_ids.read(
                [
                    "id",
                    "dependency_level",
                    "activity_type",
                    "goal",
                    "action",
                    "observation",
                    "result",
                ]
            )

    def _compute_resident_data(self):
        for record in self:
            record.resident = record.resident_id.read(
                [
                    "id",
                    "name",
                ]
            )[0] 

    