# -*- coding: utf-8 -*-
import logging
import re
from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SupplierCategory(models.Model):
    _name = 'supplier.category'
    _description = 'Categoría de los proveedores'
    _order = 'name'
    _rec_name = 'name'

    name = fields.Char(
        string='Nombre de Categoría',
        required=True,
        help='Nombre de la categoría del proveedor'
    )
    description = fields.Text(
        string='Descripción',
        help='Descripción detallada de la categoria'
    )
    active = fields.Boolean(
        string='Activo',
        default=True,
        help='Si está desmarcado, la categoría no aparecerá en las opciones'
    )
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

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, f"{record.name}"))
        return result

    @api.model
    def create(self, vals):
        for vals in vals:
            existing_record_slug = self.search(
                [
                    ("slug", "=", self._generate_slug(vals.get("name"))),
                ],
                limit=1,
            )

            if existing_record_slug:
                raise ValidationError(
                    f"Ya existe una categoría con el nombre '{vals['name']}'."
                )

        records = super().create(vals)
        # Crear log de auditoría para cada registro creado
        for record in records:
            self.env['audit.log'].sudo().crud_audit_log(record, 'supplier.category', 'create')
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
                    f"Ya existe una categoría con el nombre '{vals['name']}'."
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
            self.env['audit.log'].sudo().crud_audit_log(record, 'supplier.category', 'write', extra_details=details)
        return result
    
    def unlink(self):
        # Antes de eliminar, crear logs para cada registro
        for record in self:
            self.env['audit.log'].sudo().crud_audit_log(record, 'supplier.category', 'unlink')
        return super().unlink()
