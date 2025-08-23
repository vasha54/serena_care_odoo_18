import logging
import re

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class WaterBalanceRoute(models.Model):
    _name = "water.balance.route"
    _description = "Via por la que ocurre el ingreso o egreso de líquido"

    name = fields.Char(string="Nombre", required=True)
    slug = fields.Char(
        string="Slug", compute="_compute_slug", readonly=True, store=True
    )
    annotation_ids = fields.One2many(
        "water.balance.annotation",
        "route_id",
        string="Anotaciones del balance híbrido que usan esta vía ingreso/egreso",
    )

    @api.depends("name")
    def _compute_slug(self):
        for record in self:
            record.slug = self._generate_slug(record.name)

    def _generate_slug(self, name):
        cleaned = re.sub(r"[^\w\-]+", "", str(name))
        slug = cleaned.replace(" ", "-")
        return slug.lower()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            existing_record_slug = self.search(
                [
                    ("slug", "=", self._generate_slug(vals.get("name"))),
                ],
                limit=1,
            )

            if existing_record_slug:
                raise ValidationError(
                    f"Una vía de ingreso/egreso con nombre '{vals['name']}' ya existe."
                )

        return super().create(vals_list)

    def write(self, vals):
        if "name" in vals:
            existing_record_slug = self.search(
                [
                    ("slug", "=", self._generate_slug(vals.get("name"))),
                    ("id", "!=", self.id),
                ],
                limit=1,
            )

            if existing_record_slug:
                raise ValidationError(
                    f"Una vía de ingreso/egreso con nombre '{vals['name']}' ya existe."
                )

        return super().write(vals)

    def unlink(self):
        for route in self:
            if route.annotation_ids:
                residents_name = route.annotation_ids.mapped("resident_id.name")
                raise UserError(
                    _(
                        "No se puede eliminar la vía de ingreso/egreso %s porque está siendo utilizado en:\n- %s"
                    )
                    % (route.name, "\n- ".join(residents_name))
                )
        return super().unlink()

    def toggle_active(self):
        for route in self:
            if route.active and route.annotation_ids:
                raise UserError(
                    "No se puede desactivar una vía de ingreso/egreso que está en uso en anotaciones del balance híbrido"
                )
        return super().toggle_active()
