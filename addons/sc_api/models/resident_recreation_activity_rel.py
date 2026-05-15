import logging
import re
import os
import base64
from dateutil.relativedelta import relativedelta
from datetime import date

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)

class ResidentRecreationalActivityRel(models.Model):
    _inherit = 'resident.recreation.activity.rel'
    
    activity_type = fields.Json(
        string="Actividad Tipo Datos",
        compute="_compute_activity_type_data",
        store=False,
    )
    activity = fields.Json(
        string="Actividad Datos",
        compute="_compute_activity_data",
        store=False,
    )
    user = fields.Json(
        string="Usuario Datos",
        compute="_compute_user_data",
        store=False,
    )
    resident = fields.Json(
        string="Residente Datos",
        compute="_compute_resident_data",
        store=False,
    )

    def _compute_activity_type_data(self):
        for record in self:
            record.activity_type = record.activity_type_id.read(
                [
                    "id",
                    "name",
                ]
            )[0]

    def _compute_activity_data(self):
        for record in self:
            record.activity = record.activity_id.read(
                [
                    "id",
                ]
            )[0]
    
    def _compute_user_data(self):
        for record in self:
            record.user = record.user_id.read(
                [
                    "id",
                    "name",
                ]
            )[0]

    def _compute_resident_data(self):
        for record in self:
            record.resident = record.resident_id.read(
                [
                    "id",
                    "name",
                ]
            )[0]

    