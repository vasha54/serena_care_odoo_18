import re
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)

class RouteAdministration(models.Model):
    _name = 'route.administration'

    name =  fields.Char(string="Nombre", required=True, upper=True)
    slug = fields.Char(
        string="Slug", compute="_compute_slug", readonly=True, store=True
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
            vals['name'] = vals.get('name', '').upper()
            existing_record_slug = self.search(
                [
                    ("slug", "=", self._generate_slug(vals.get("name"))),
                ],
                limit=1,
            )

            if existing_record_slug:
                raise ValidationError(
                    f"Una vía de administración con nombre '{vals['name']}' ya existe."
                )


        return super().create(vals_list)

    def write(self, vals):
        if "name" in vals:
            vals['name'] = vals['name'].upper()
            existing_record_slug = self.search(
                [
                    ("slug", "=", self._generate_slug(vals.get("name"))),
                    ("id", "!=", self.id),
                ],
                limit=1,
            )

            if existing_record_slug:
                raise ValidationError(
                    f"Una vía de administración con nombre '{vals['name']}' ya existe."
                )

        return super().write(vals)