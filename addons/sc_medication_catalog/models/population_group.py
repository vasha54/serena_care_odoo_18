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

    @api.model
    def create(self, values):
        # Normalizar entrada: si es un solo dict, convertirlo a lista
        if not isinstance(values, list):
            values = [values]
            
        for vals in values:
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
        records = super().create(values)
        # Crear log de auditoría para cada registro creado
        for record in records:
            self.env['audit.log'].sudo().crud_audit_log(record, 'population.group', 'create')
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
                    f"Un grupo poblacional con nombre '{vals['name']}' ya existe."
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
            self.env['audit.log'].sudo().crud_audit_log(record, 'population.group', 'write', extra_details=details)
        return result

    def unlink(self):
        for group in self:
            if group.dosage_ids:
                medicamentos = group.dosage_ids.mapped('medicament_id.name')
                raise UserError(
                    _("No se puede eliminar el grupo poblacional %s porque está siendo utilizado en:\n- %s") % 
                    (group.name, "\n- ".join(medicamentos))
                )
        # Antes de eliminar, crear logs para cada registro
        for record in self:
            self.env['audit.log'].sudo().crud_audit_log(record, 'population.group', 'unlink')
        return super().unlink()

    def toggle_active(self):
        for group in self:
            if group.active and group.dosage_ids:
                raise UserError(
                    "No se puede desactivar un grupo poblacional que está en uso en medicamentos"
                )
        return super().toggle_active()
