import re
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError

import logging
_logger = logging.getLogger(__name__)

class PharmaceuticalForm(models.Model):
    _name = 'pharmaceutical.form'

    active = fields.Boolean(string='Activa', default=True)
    name =  fields.Char(string="Nombre", required=True)
    slug = fields.Char(
        string="Slug", compute="_compute_slug", readonly=True, store=True
    )
    # medicament_ids = fields.One2many(
    #     'medicament.product', 
    #     'pharmaceutical_form_id', 
    #     string='Medicamentos que usan esta forma farmacéutica'
    # )

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
            vals['name'] = vals.get('name', '')
            existing_record_slug = self.search(
                [
                    ("slug", "=", self._generate_slug(vals.get("name"))),
                ],
                limit=1,
            )

            if existing_record_slug:
                raise ValidationError(
                    f"Una forma farmacéutica con nombre '{vals['name']}' ya existe."
                )
        records = super().create(values)
        # Crear log de auditoría para cada registro creado
        for record in records:
            self.env['audit.log'].sudo().crud_audit_log(record, 'pharmaceutical.form', 'create')
        return records

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
                    f"Una forma farmacéutica con nombre '{vals['name']}' ya existe."
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
            self.env['audit.log'].sudo().crud_audit_log(record, 'pharmaceutical.form', 'write', extra_details=details)
        return result

    def unlink(self):
        # Antes de eliminar, crear logs para cada registro
        for record in self:
            self.env['audit.log'].sudo().crud_audit_log(record, 'pharmaceutical.form', 'unlink')
        return super().unlink()

    def toggle_active(self):
        for form_show in self:
            if form_show.active and form_show.medicament_ids:
                raise UserError(
                    "No se puede desactivar una forma de farmacéutica que está en uso en medicamentos"
                )
        return super().toggle_active()