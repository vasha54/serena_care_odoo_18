import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)

class LawtonBrodyChoise(models.Model):
    _name = 'lawtonbrody.choise'
    _description = 'Opción de respuesta a una pregunta de Lawton-Brody'

    name = fields.Char(string='Opción', required=True)
    value = fields.Float(string='Valor', required=True)
    question_ids = fields.Many2many('lawtonbrody.question', string='Preguntas')

    @api.constrains('name', 'value')
    def _check_unique_option(self):
        for record in self:
            existing_options = self.search([
                ('name', '=', record.name),
                ('value', '=', record.value),
                ('id', '!=', record.id)  # Exclude the current record
            ])
            if existing_options:
                raise ValidationError("Ya existe una opción con el mismo nombre y valor.")

    @api.model
    def create(self, vals):
        self._check_unique_option()
        records = super(LawtonBrodyChoise, self).create(vals)
        # Crear log de auditoría para cada registro creado
        for record in records:
            self.env['audit.log'].sudo().crud_audit_log(record, 'lawtonbrody.choise', 'create')
        return records

    def write(self, vals):
        self._check_unique_option()
        # Guardar estado anterior para detectar cambios (opcional, mejora la calidad del detalle)
        old_values = {}
        for record in self:
            old_values[record.id] = {
                field: record[field] for field in vals if field in record._fields and not record._fields[field].compute
            }
        result = super(LawtonBrodyChoise, self).write(vals)
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
            self.env['audit.log'].sudo().crud_audit_log(record, 'lawtonbrody.choise', 'write', extra_details=details)
        return result

    def unlink(self):
        for record in self:
            # Verificar si está asociado a preguntas
            if record.question_ids:
                raise ValidationError("No se puede eliminar una opción que está asociada a preguntas.")

            # Verificar si está asociado a respuestas
            answer_count = self.env['lawtonbrody.answer'].search_count([
                ('choise_select_id', '=', record.id)
            ])
            if answer_count > 0:
                raise ValidationError("No se puede eliminar una opción que está siendo utilizada en respuestas.")
        # Antes de eliminar, crear logs para cada registro
        for record in self:
            self.env['audit.log'].sudo().crud_audit_log(record, 'lawtonbrody.choise', 'unlink')
        return super(LawtonBrodyChoise, self).unlink()
