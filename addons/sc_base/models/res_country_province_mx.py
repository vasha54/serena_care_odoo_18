# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class ResProvinceMX(models.Model):
    _name = "res_province_mx"
    _description = "Modelo que representa los diferentes estados o provincias donde se ubican las residencias"
    _inherit = ["res_country_mx"]

    municipality_ids = fields.One2many(
        string="Municipios",
        comodel_name="res_municipality_mx",
        inverse_name="province_id",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            existing_record_slug = self.search(
                [
                    ("slug", "=", self._generate_slug(vals.get("name"))),
                    ("country_id", "=", vals.get("country_id")),
                ],
                limit=1,
            )

            if existing_record_slug:
                raise ValidationError(
                    f"Ya existe un estado con el nombre '{vals['name']}' en el país '{vals['country_id']}'."
                )

        return super(ResProvinceMX, self).create(vals_list)

    def write(self, vals):
        if "name" in vals or "country_id" in vals:
            existing_record_slug = self.search(
                [
                    ("slug", "=", self._generate_slug(vals.get("name"))),
                    ("id", "!=", self.id),
                    ("country_id", "=", self.country_id),
                ],
                limit=1,
            )

            if existing_record_slug:
                raise ValidationError(
                    f"Ya existe un estado con el nombre '{vals['name']}' en el país '{vals['country_id']}'."
                )

        return super(ResProvinceMX, self).write(vals)
