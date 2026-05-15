import logging
import re
import os
import base64
from dateutil.relativedelta import relativedelta
from datetime import date

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)

class NomenclatureActivityType(models.Model):
    _name = 'nomenclature.activity.type'

    active = fields.Boolean(string='Activa', default=True)
    name =  fields.Char(string="Nombre", required=True)
    slug = fields.Char(
        string="Slug", compute="_compute_slug", readonly=True, store=True
    )
    activity_ids = fields.One2many(
        'recreational.activity', 
        'activity_type_id',
        string="Activiades recreativas",
        help="Actividades asociadas a este tipo de actividad")
    image = fields.Binary(
        string="Imagen",
        attachment=True,
        help="Imagen asociada al tipo de actividad"
    )
    image_with_default = fields.Binary(
        string="Imagen con valor por defecto",
        compute="_compute_image_with_default",
        store=False,
    )

    @api.depends("image")
    def _compute_image_with_default(self):
        default_image_path = os.path.join(
            os.path.dirname(__file__), "..", "static","src", "img", "activity_types",
            "type_activity_default.png"
        )
        # Leer la imagen por defecto si existe
        default_image = None
        if os.path.exists(default_image_path):
            with open(default_image_path, "rb") as f:
                default_image = base64.b64encode(f.read())

        for record in self:
            if record.image:
                record.image_with_default = record.image
            else:
                record.image_with_default = default_image

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
                    f"Un tipo de actividad con nombre '{vals['name']}' ya existe."
                )
        records = super().create(values)
        # Crear log de auditoría para cada registro creado
        for record in records:
            self.env['audit.log'].sudo().crud_audit_log(record, 'nomenclature.activity.type', 'create')
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
                    f"Un tipo de actividad con nombre '{vals['name']}' ya existe."
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
            self.env['audit.log'].sudo().crud_audit_log(record, 'nomenclature.activity.type', 'write', extra_details=details)
        return result

    def unlink(self):
        for record in self:
            if record.activity_ids:
                activitys =record.activity_ids.mapped('display_name')
                raise UserError(
                    _("No se puede eliminar el tipo de actividad %s porque está siendo utilizado en:\n- %s") % 
                    (record.name, "\n- ".join(activitys))
                )
        # Antes de eliminar, crear logs para cada registro
        for record in self:
            self.env['audit.log'].sudo().crud_audit_log(record, 'nomenclature.activity.type', 'unlink')
        return super().unlink()

    def toggle_active(self):
        for record in self:
            if record.active and record.activity_ids:
                raise UserError(
                    "No se puede desactivar un tipo de actividad que está en uso."
                )
        return super().toggle_active()
