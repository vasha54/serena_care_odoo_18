import re
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError

import logging
_logger = logging.getLogger(__name__)

class AdministrationRoute(models.Model):
    _name = 'administration.route'

    active = fields.Boolean(string='Activa', default=True)
    name =  fields.Char(string="Nombre", required=True)
    slug = fields.Char(
        string="Slug", compute="_compute_slug", readonly=True, store=True
    )
    dosage_ids = fields.One2many(
        'medicament.dosage', 
        'route_id', 
        string='Dosis que usan esta vía administrativa'
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
                    f"Una vía de administración con nombre '{vals['name']}' ya existe."
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
                    f"Una vía de administración con nombre '{vals['name']}' ya existe."
                )

        return super().write(vals)

    def unlink(self):
        for route in self:
            if route.dosage_ids:
                medicamentos = route.dosage_ids.mapped('medicament_id.name')
                raise UserError(
                    _("No se puede eliminar la via de administración %s porque está siendo utilizado en:\n- %s") % 
                    (route.name, "\n- ".join(medicamentos))
                )
        return super().unlink()

    def toggle_active(self):
        for route in self:
            if route.active and route.dosage_ids:
                raise UserError(
                    "No se puede desactivar una vía de administración que está en uso en medicamentos"
                )
        return super().toggle_active()