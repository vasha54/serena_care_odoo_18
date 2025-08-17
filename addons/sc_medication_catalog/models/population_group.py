from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError

import logging
import re

_logger = logging.getLogger(__name__)

class PopulationGroup(models.Model):
    _name = 'population.group'
    _description = 'Grupo Poblacional sobre la cual se aplica el medicamento'
    _order = 'name asc'

    active = fields.Boolean(string='Activa', default=True)
    name = fields.Char(string='Nombre', required=True)
    slug = fields.Char(
        string="Slug", compute="_compute_slug", readonly=True, store=True
    )
    dosage_ids = fields.One2many(
        'medicament.dosage', 
        'population_group_id', 
        string='Dosis que usan este grupo poblacional'
    )

    _sql_constraints = [
        ('name_slug_population_group', 
         'UNIQUE(slug)', 
         '¡El nombre del grupo poblacional ya existe (ignorando mayúsculas/minúsculas)!')
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
                    f"Un grupo poblacional con nombre '{vals['name']}' ya existe."
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
                    f"Un grupo poblacional con nombre '{vals['name']}' ya existe."
                )

        return super().write(vals)

    def unlink(self):
        for group in self:
            if group.dosage_ids:
                medicamentos = group.dosage_ids.mapped('medicament_id.name')
                raise UserError(
                    _("No se puede eliminar el grupo poblacional %s porque está siendo utilizado en:\n- %s") % 
                    (group.name, "\n- ".join(medicamentos))
                )
        return super().unlink()

    def toggle_active(self):
        for group in self:
            if group.active and group.dosage_ids:
                raise UserError(
                    "No se puede desactivar un grupo poblacional que está en uso en medicamentos"
                )
        return super().toggle_active()
