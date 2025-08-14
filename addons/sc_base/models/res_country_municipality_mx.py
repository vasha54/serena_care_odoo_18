# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResMunicipalityMX(models.Model):
    _name = "res_municipality_mx"
    _description = "Modelo que representa los diferentes municipios donde se ubican los actores económicos"
    _inherit = ["res_country_mx"]

    province_id = fields.Many2one(
        "res_province_mx",
        string="Estado",
        ondelete="restrict",
    )

    code = fields.Char(string="Código", required=False)

    @api.onchange("province_id")
    def _onchange_code(self):
        self.country_id = self.province_id.country_id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            existing_record_slug = self.search(
                [
                    ("slug", "=", self._generate_slug(vals.get("name"))),
                    ("province_id", "=", vals.get("province_id")),
                ],
                limit=1,
            )

            if existing_record_slug:
                raise ValidationError(
                    f"Ya existe un municipio con nombre '{vals['name']}' en la provincia '{vals['province_id']}'."
                )

        return super(ResMunicipalityMX, self).create(vals_list)

    def write(self, vals):
        if "name" in vals or "province_id" in vals:
            existing_record_slug = self.search(
                [
                    ("slug", "=", self._generate_slug(vals.get("name"))),
                    ("id", "!=", self.id),
                    ("province_id", "=", self.province_id),
                ],
                limit=1,
            )

            if existing_record_slug:
                raise ValidationError(
                    f"Ya existe un municipio con el nombre '{vals['name']}' en la provincia '{vals['province_id']}'."
                )

        return super(ResMunicipalityMX, self).write(vals)

    @api.model
    def name_get(self):
        result = []
        for state in self:
            name = f"{state.name}"
            result.append((state.id, name))
        return result
