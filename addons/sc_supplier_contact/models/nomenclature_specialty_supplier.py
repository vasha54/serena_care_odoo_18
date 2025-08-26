import re
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError

import logging
_logger = logging.getLogger(__name__)

class NomenclatureSpecialtySupplier(models.Model):
    _name = 'nomenclature.specialty.supplier'

    active = fields.Boolean(string='Activa', default=True)
    name =  fields.Char(string="Nombre", required=True)
    slug = fields.Char(
        string="Slug", compute="_compute_slug", readonly=True, store=True
    )
    suppliers_ids = fields.One2many(
        'supplier.base', 
        'nomenclature_specialty_id', 
        string='Proveedores que estan usando este especialidad'
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
            vals['name'] = vals.get('name', '')
            existing_record_slug = self.search(
                [
                    ("slug", "=", self._generate_slug(vals.get("name"))),
                ],
                limit=1,
            )

            if existing_record_slug:
                raise ValidationError(
                    f"Una especialidad con nombre '{vals['name']}' ya existe."
                )


        return super().create(vals_list)

    def write(self, vals):
        if "name" in vals:
            vals['name'] = vals['name']
            existing_record_slug = self.search(
                [
                    ("slug", "=", self._generate_slug(vals.get("name"))),
                    ("id", "!=", self.id),
                ],
                limit=1,
            )

            if existing_record_slug:
                raise ValidationError(
                    f"Una especialidad con nombre '{vals['name']}' ya existe."
                )

        return super().write(vals)

    def unlink(self):
        for record in self:
            if record.suppliers_ids:
                suppliers =record.suppliers_ids.mapped('name')
                raise UserError(
                    _("No se puede eliminar la especialidad %s porque está siendo utilizado en:\n- %s") % 
                    (record.name, "\n- ".join(suppliers))
                )
        return super().unlink()

    def toggle_active(self):
        for record in self:
            if record.active and record.suppliers_ids:
                raise UserError(
                    "No se puede desactivar una especialidad que está en uso."
                )
        return super().toggle_active()