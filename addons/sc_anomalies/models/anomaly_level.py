import re
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError

import logging
_logger = logging.getLogger(__name__)

class AnomalyLevel(models.Model):
    _name = 'anomaly.level'
    _description = 'Nivel de Anomalía'
   
    active = fields.Boolean(string='Activo', default=True)
    name = fields.Char(string="Nivel", required=True)
    description = fields.Text(string="Descripción")
    sequence = fields.Integer(string="Orden", default=1)
    slug = fields.Char(
        string="Slug", compute="_compute_slug", readonly=True, store=True
    )
    color = fields.Char(string="Color", required=True)

    _sql_constraints = [
        ('color_level_anomaly', 'unique(color)', 'Este color ya esta siendo utilizado')
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
                    f"Un nivel de anomalía con nombre '{vals['name']}' ya existe."
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
                    f"Un nivel de anonamalía con nombre '{vals['name']}' ya existe."
                )

        return super().write(vals)

    def unlink(self):
        # Obtener el XML ID del registro crítico
        critical_record = self.env.ref('sc_anomalies.alevel_critical', raise_if_not_found=False)
        
        # Verificar si alguno de los registros que se intentan eliminar es el crítico
        for record in self:
            if critical_record and record.id == critical_record.id:
                raise UserError(_('No se puede eliminar el nivel de anomalía "Crítica" porque está comprometido para otras funciones u operaciones del sistema.'))
        
        return super().unlink()

    def toggle_active(self):
        # Opcional: También evitar desactivar el registro crítico
        critical_record = self.env.ref('sc_anomalies.alevel_critical', raise_if_not_found=False)
        
        for record in self:
            if critical_record and record.id == critical_record.id and not record.active:
                raise UserError(_('No se puede desactivar el nivel de anomalía "Crítica" porque está comprometido para otras funciones u operaciones del sistema.'))
        
        return super().toggle_active()