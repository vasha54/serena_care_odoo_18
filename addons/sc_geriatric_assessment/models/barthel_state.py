import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)

class BarthelState(models.Model):
    _name = 'barthel.state'
    _description = 'Estado de Barthel'
    _order = 'min_score asc'  # Ordenar por puntuación de forma ascendente

    active = fields.Boolean(string='Activo', default=True, help="Desmarcar para archivar el estado.")
    name = fields.Char(string='Interpretación', required=True, help="Ejemplo: Depresión leve")
    min_score = fields.Integer(string='Puntuación Mínima', required=True, help="Límite inferior del rango, ej: 0")
    max_score = fields.Integer(string='Puntuación Máxima', required=True, help="Límite superior del rango, ej: 4")

    @api.constrains('min_score', 'max_score')
    def _check_score_range(self):
        for record in self:
            if record.min_score > record.max_score:
                raise ValidationError("La puntuación mínima no puede ser mayor que la máxima.")
            # Buscar si hay rangos que se solapan con otros estados
            # overlapping = self.search([
            #     ('id', '!=', record.id),
            #     ('active', '=', True),
            #     '|', '|',
            #     ('min_score', '<=', record.max_score, 'and', 'max_score', '>=', record.min_score),
            #     ('min_score', '<=', record.min_score, 'and', 'max_score', '>=', record.min_score),
            #     ('min_score', '<=', record.max_score, 'and', 'max_score', '>=', record.max_score)
            # ], limit=1)
            # if overlapping:
            #     raise ValidationError(f"Este rango se solapa con el estado '{overlapping.name}'. Los rangos no deben superponerse.")

    @api.model
    def create(self, values):
        records = super().create(values)
        # Crear log de auditoría para cada registro creado
        for record in records:
            self.env['audit.log'].sudo().crud_audit_log(record, 'barthel.state', 'create')
        return records
    
    def write(self, vals):
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
            self.env['audit.log'].sudo().crud_audit_log(record, 'barthel.state', 'write', extra_details=details)
        return result
    
    def unlink(self):
        # Antes de eliminar, crear logs para cada registro
        for record in self:
            self.env['audit.log'].sudo().crud_audit_log(record, 'barthel.state', 'unlink')
        return super().unlink()
