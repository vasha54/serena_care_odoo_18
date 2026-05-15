import logging
import re
import os
import base64
from dateutil.relativedelta import relativedelta
from datetime import date

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class NomenclatureAddiction(models.Model):
    _name = 'nomenclature.addiction'

    active = fields.Boolean(string='Activa', default=True)
    name =  fields.Char(string="Nombre", required=True)
    slug = fields.Char(
        string="Slug", compute="_compute_slug", readonly=True, store=True
    )
    resident_ids = fields.Many2many(
        comodel_name='resident',
        relation='model_resident_addiction_ref',
        string="Residentes",
        help='Residentes que padecen esta adicción'
    )

    _sql_constraints = [
        ('name_unique_addiction', 'UNIQUE(name)', 'El nombre de la adicción debe ser único.'),
    ]

    @api.depends("name")
    def _compute_slug(self):
        for record in self:
            record.slug = self._generate_slug(record.name)

    def _generate_slug(self, name):
        if not name:
            return ''
        cleaned = re.sub(r"[^\w\-]+", "", str(name))
        slug = cleaned.replace(" ", "-")
        return slug.lower()

    @api.model
    def create(self, vals_list):
        # Normalizar entrada: si es un solo dict, convertirlo a lista
        if not isinstance(vals_list, list):
            vals_list = [vals_list]
        
        for vals in vals_list:
            name = vals.get('name', '')
            # Validar unicidad por slug (opcional, pero consistente)
            slug = self._generate_slug(name)
            existing_record_slug = self.search([("slug", "=", slug)], limit=1)
            if existing_record_slug:
                raise ValidationError(
                    f"Una adicción con nombre '{name}' ya existe."
                )
        
        records = super().create(vals_list)
        
        for record in records:
            self.env['audit.log'].sudo().crud_audit_log(record, 'nomenclature.addiction', 'create')
        
        return records

    def write(self, vals):
        if "name" in vals:
            new_name = vals['name']
            new_slug = self._generate_slug(new_name)
            # Buscar cualquier otro registro (que no esté en el recordset actual) con el mismo slug
            existing = self.search([
                ("slug", "=", new_slug),
                ("id", "not in", self.ids)
            ], limit=1)
            if existing:
                raise ValidationError(
                    f"Una adicción con nombre '{new_name}' ya existe."
                )
        
        # Guardar estado anterior para auditoría
        old_values = {}
        for record in self:
            old_values[record.id] = {
                field: record[field] for field in vals if field in record._fields and not record._fields[field].compute
            }
        result = super().write(vals)
        
        # Log de auditoría
        for record in self:
            changed_fields = []
            for field, new_val in vals.items():
                if field in old_values.get(record.id, {}):
                    old_val = old_values[record.id][field]
                    if old_val != record[field]:
                        changed_fields.append(f"{field}: {old_val!r} -> {record[field]!r}")
                else:
                    changed_fields.append(f"{field}: {record[field]!r}")
            if changed_fields:
                details = "Campos modificados: " + "; ".join(changed_fields)
            else:
                details = "Modificación sin cambios detectados"
            self.env['audit.log'].sudo().crud_audit_log(record, 'nomenclature.addiction', 'write', extra_details=details)
        
        return result

    def unlink(self):
        for record in self:
            if record.resident_ids:
                residents =record.resident_ids.mapped('name')
                raise UserError(
                    _("No se puede eliminar la adicción %s porque está siendo utilizado en:\n- %s") %
                    (record.name, "\n- ".join(residents))
                )
        # Antes de eliminar, crear logs para cada registro
        for record in self:
            self.env['audit.log'].sudo().crud_audit_log(record, 'nomenclature.addiction', 'unlink')
        return super().unlink()

    def toggle_active(self):
        for record in self:
            if record.active and record.resident_ids:
                raise UserError(
                    "No se puede desactivar una adicción que está en uso."
                )
        return super().toggle_active()
