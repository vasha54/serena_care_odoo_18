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

    @api.model
    def create(self, values):
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
                    f"Una especialidad con nombre '{vals['name']}' ya existe."
                )
        records = super().create(values)
        # Crear log de auditoría para cada registro creado
        for record in records:
            self.env['audit.log'].sudo().crud_audit_log(record, 'nomenclature.specialty.supplier', 'create')
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
                    f"Una especialidad con nombre '{vals['name']}' ya existe."
                )
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
            self.env['audit.log'].sudo().crud_audit_log(record, 'nomenclature.specialty.supplier', 'write', extra_details=details)
        return result

    def unlink(self):
        for record in self:
            if record.suppliers_ids:
                suppliers =record.suppliers_ids.mapped('name')
                raise UserError(
                    _("No se puede eliminar la especialidad %s porque está siendo utilizado en:\n- %s") % 
                    (record.name, "\n- ".join(suppliers))
                )
        # Antes de eliminar, crear logs para cada registro
        for record in self:
            self.env['audit.log'].sudo().crud_audit_log(record, 'nomenclature.specialty.supplier', 'unlink')
        return super().unlink()

    def toggle_active(self):
        for record in self:
            if record.active and record.suppliers_ids:
                raise UserError(
                    "No se puede desactivar una especialidad que está en uso."
                )
        return super().toggle_active()