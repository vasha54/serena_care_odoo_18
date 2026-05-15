import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)

class Resident(models.Model):
    _inherit = "resident"

    sex = fields.Json(
        string="Sexo",
        compute="_compute_sex_data",
        store=False,
    )
    residence = fields.Json(
        string="Resdencia",
        compute="_compute_residence_data",
        store=False,
    )
    country = fields.Json(
        string="Pais",
        compute="_compute_country_data",
        store=False,
    )
    province = fields.Json(
        string="Estado",
        compute="_compute_province_data",
        store=False,
    )
    municipality = fields.Json(
        string="Municipio",
        compute="_compute_municipality_data",
        store=False,
    )
    addictions = fields.Json(
        string="Adicciones",
        compute="_compute_addictions_data",
        store=False,
    )
    allergys = fields.Json(
        string="Alergías",
        compute="_compute_allergys_data",
        store=False,
    )

    def _compute_sex_data(self):
        for record in self:
            record.sex = record.sex_id.read(
                [
                    "id",
                    "name",
                ]
            )[0]

    def _compute_residence_data(self):
        for record in self:
            record.residence = record.residence_id.read(
                [
                    "id",
                    "name",
                ]
            )[0]

    def _compute_country_data(self):
        for record in self:
            record.country = record.country_id.read(
                [
                    "id",
                    "name",
                ]
            )[0]

    def _compute_province_data(self):
        for record in self:
            record.province = record.province_id.read(
                [
                    "id",
                    "name",
                ]
            )[0]

    def _compute_municipality_data(self):
        for record in self:
            record.municipality = record.municipality_id.read(
                [
                    "id",
                    "name",
                ]
            )[0]

    def _compute_addictions_data(self):
        for record in self:
            record.addictions = record.addiction_ids.read(
                [
                    "id",
                    "name",
                ]
            )

    def _compute_allergys_data(self):
        for record in self:
            record.allergys = record.allergy_ids.read(
                [
                    "id",
                    "name",
                ]
            )