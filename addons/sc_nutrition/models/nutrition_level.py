import re
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError

import logging
_logger = logging.getLogger(__name__)

class NutritionLevel(models.Model):
    _name = 'nutrition.level'
    _description = 'Nivel de alimentación'
   
    active = fields.Boolean(string='Activo', default=True)
    name = fields.Char(string="Nivel", required=True)
    description = fields.Text(string="Descripción")
    slug = fields.Char(
        string="Slug", compute="_compute_slug", readonly=True, store=True
    )
    percent = fields.Float(
        string='Porciento de alimento ingerido',
        help="Indica en porciento de la cantidad de alimento ingerida por un residente de una ración de alimentos suministrada"
    )
    
    _sql_constraints = [
        ('percent_level_nutrition', 'unique(percent)', 'Este valor ya está siendo usado')
    ]

    @api.depends("name")
    def _compute_slug(self):
        for record in self:
            record.slug = self._generate_slug(record.name)

    @api.constrains('percent')
    def _check_unique_activity_per_plan(self):
        for record in self:
            if record.percent and (record.percent < 0 or 100 < record.percent):
                raise ValidationError("Valor del porciento debe estar entre 0 y 100.")

    def _generate_slug(self, name):
        cleaned = re.sub(r"[^\w\-]+", "", str(name))
        slug = cleaned.replace(" ", "-")
        return slug.lower()

    @api.model
    def create(self, vals):
        # Normalizar entrada: si es un solo dict, convertirlo a lista
        if not isinstance(vals, list):
            vals = [vals]
            
        for vals in vals:
            existing_record_slug = self.search(
                [
                    ("slug", "=", self._generate_slug(vals.get("name"))),
                ],
                limit=1,
            )

            if existing_record_slug:
                raise ValidationError(
                    f"Un nivel de alimentación con nombre '{vals['name']}' ya existe."
                )
        records = super().create(vals)
        # Crear log de auditoría para cada registro creado
        for record in records:
            self.env['audit.log'].sudo().crud_audit_log(record, 'nutrition.level', 'create')
        return records

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
                    f"Un nivel de alimentación con nombre '{vals['name']}' ya existe."
                )

        # Guardar estado anterior para detectar cambios (opcional, mejora la calidad del detalle)
        old_values = {}
        for record in self:
            old_values[record.id] = {
                field: record[field] for field in vals if field in record._fields and not record._fields[field].compute
            }
        result = super().write(vals)
        # Después de la escritura, crear logs con los campos modificados
        for record in self:
            changed_fields = []
            for field, new_val in vals.items():
                if field in old_values.get(record.id, {}):
                    old_val = old_values[record.id][field]
                    if old_val != record[field]:
                        changed_fields.append(f"{field}: {old_val!r} -> {record[field]!r}")
                else:
                    # Campo no almacenado o no presente en el registro anterior, se registra igual
                    changed_fields.append(f"{field}: {record[field]!r}")
            if changed_fields:
                details = "Campos modificados: " + "; ".join(changed_fields)
            else:
                details = "Modificación sin cambios detectados"
            self.env['audit.log'].sudo().crud_audit_log(record, 'nutrition.level', 'write', extra_details=details)
        return result

    def unlink(self):
        # Antes de eliminar, crear logs para cada registro
        for record in self:
            self.env['audit.log'].sudo().crud_audit_log(record, 'nutrition.level', 'unlink')
        return super().unlink()

    def toggle_active(self):
        return super().toggle_active()


