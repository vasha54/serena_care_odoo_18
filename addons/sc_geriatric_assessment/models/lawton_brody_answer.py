import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class LawtonBrodyAnswer(models.Model):
    _name = "lawtonbrody.answer"
    _description = "Respuesta del residente ante la pregunta"

    resident_id = fields.Many2one("resident", string="Residente", required=True)

    user_id = fields.Many2one(
        "res.users",
        string="Registrado por",
        default=lambda self: self.env.user,
        required=True,
        ondelete="restrict",
    )
    assessment_id = fields.Many2one(
        "lawtonbrody.assessment", string="Evaluación", required=True
    )
    choise_select_id = fields.Many2one(
        "lawtonbrody.choise", string="Opción seleccionada", required=True
    )
    choise_select_value = fields.Float(
        related="choise_select_id.value", string="Puntuación", readonly=True
    )
    choise_select_name = fields.Char(
        related="choise_select_id.name", string="Nombre", readonly=True
    )
    question_id = fields.Many2one(
        "lawtonbrody.question", string="Actividad", required=True
    )
    question_name = fields.Char(
        related="question_id.name", string="Actividad", readonly=True
    )

    @api.depends("question_id", "create_date")
    def _compute_display_name(self):
        for r in self:
            r.display_name = f"Respuesta dada a la pregunta: {r.question_id.name} realizada {r.create_date.strftime('%Y-%m-%d %H:%M')}"

    @api.model
    def create(self, values):
        records = super().create(values)
        # Crear log de auditoría para cada registro creado
        for record in records:
            self.env['audit.log'].sudo().crud_audit_log(record, 'lawtonbrody.answer', 'create')
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
            self.env['audit.log'].sudo().crud_audit_log(record, 'lawtonbrody.answer', 'write', extra_details=details)
        return result
    
    def unlink(self):
        # Antes de eliminar, crear logs para cada registro
        for record in self:
            self.env['audit.log'].sudo().crud_audit_log(record, 'lawtonbrody.answer', 'unlink')
        return super().unlink()