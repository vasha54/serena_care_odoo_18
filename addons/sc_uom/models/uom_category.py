import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)

class UoMCategory(models.Model):
    _inherit = 'uom.category'

    is_uom_sc = fields.Boolean(
        string="Es Categoría de Serena Care",
        help="Categoría gestionada por Serena - Care",
        default=False
    )

    @api.model
    def create(self, values):
        # Lógica original para marcar como categoría de Serena Care si viene en el contexto
        if 'uom_sc' in self.env.context:
            values['is_uom_sc'] = True
        records = super().create(values)
        # Crear log de auditoría para cada registro creado
        for record in records:
            self.env['audit.log'].sudo().crud_audit_log(record, 'uom.category', 'create')
        return records

    def write(self, values):
        # Guardar estado anterior para detectar cambios reales
        old_values = {}
        for record in self:
            old_values[record.id] = {
                field: record[field] for field in values 
                if field in record._fields and not record._fields[field].compute
            }
        result = super().write(values)
        # Después de la escritura, crear logs con los campos modificados
        for record in self:
            changed_fields = []
            for field, new_val in values.items():
                if field in old_values.get(record.id, {}):
                    old_val = old_values[record.id][field]
                    if old_val != record[field]:
                        changed_fields.append(f"{field}: {old_val!r} -> {record[field]!r}")
                else:
                    # Campo no almacenado o no presente en el registro anterior
                    changed_fields.append(f"{field}: {record[field]!r}")
            if changed_fields:
                details = "Campos modificados: " + "; ".join(changed_fields)
            else:
                details = "Modificación sin cambios detectados"
            self.env['audit.log'].sudo().crud_audit_log(record, 'uom.category', 'write', extra_details=details)
        return result

    def unlink(self):
        # Antes de eliminar, crear logs para cada registro
        for record in self:
            self.env['audit.log'].sudo().crud_audit_log(record, 'uom.category', 'unlink')
        return super().unlink()

    