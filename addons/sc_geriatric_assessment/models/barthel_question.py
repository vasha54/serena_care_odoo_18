import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)

class BarthelQuestion(models.Model):
    _name = 'barthel.question'
    _description = 'Pregunta para Barthel'

    active = fields.Boolean(string='Activo', default=True)
    name = fields.Char(string='Título', required=True)
    order = fields.Integer(string="Orden de secuencia", default=1)
    choise_ids = fields.Many2many('barthel.choise',
                                  string='Opciones de respuesta')
    count_choises = fields.Integer(
        string='Cant. opciones de respuestas',
        compute='_compute_count_choise',
        store = False)

    def is_option_response(self, _id_choise):
        for question in self:
            if _id_choise in question.choise_ids.mapped('id'):
                return True
        return False

    @api.depends("choise_ids")
    def _compute_count_choise(self):
        for r in self:
            if r.choise_ids:
                r.count_choises = len(r.choise_ids)
                
            
    @api.model
    def create(self, values):
        records = super().create(values)
        # Crear log de auditoría para cada registro creado
        for record in records:
            self.env['audit.log'].sudo().crud_audit_log(record, 'barthel.question', 'create')
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
            self.env['audit.log'].sudo().crud_audit_log(record, 'barthel.question', 'write', extra_details=details)
        return result
    
    def unlink(self):
        # Antes de eliminar, crear logs para cada registro
        for record in self:
            self.env['audit.log'].sudo().crud_audit_log(record, 'barthel.question', 'unlink')
        return super().unlink()


