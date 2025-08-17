from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError

import logging
import re

_logger = logging.getLogger(__name__)

class MedicamentSubstance(models.Model):
    _name = 'medicament.substance'
    _description = 'Sustancia presente en el medicamento como principio activo o excipiente'
    
    active = fields.Boolean(string='Activa', default=True)
    name = fields.Char(string='Nombre del principio activo o excipiente', required=True)
    slug = fields.Char(
        string="Slug", compute="_compute_slug", readonly=True, store=True
    )
    composition_ids = fields.One2many(
        'medicament.composition', 
        'substance_id', 
        string='Composiciones que usan esta sustancia'
    )

    _sql_constraints = [
        ('name_slug_medicament_subtances', 
         'UNIQUE(slug)', 
         '¡El nombre de la sustancia ya existe (ignorando mayúsculas/minúsculas)!')
    ]    

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
                    f"Un principio activo/excipiente con nombre '{vals['name']}' ya existe."
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
                    f"Un principio activo/excipiente con nombre '{vals['name']}' ya existe."
                )

        return super().write(vals)

    def unlink(self):
        for substance in self:
            if substance.composition_ids:
                medicamentos = substance.composition_ids.mapped('medicament_id.name')
                raise UserError(
                    _("No se puede eliminar el activo/excipiente %s porque está siendo utilizado en:\n- %s") % 
                    (substance.name, "\n- ".join(medicamentos))
                )
        return super().unlink()

    def toggle_active(self):
        for substance in self:
            if substance.active and substance.composition_ids:
                raise UserError(
                    "No se puede desactivar una sustancia que está en uso en medicamentos"
                )
        return super().toggle_active()