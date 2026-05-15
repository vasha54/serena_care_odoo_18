import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class ScaleGDS5Assessment(models.Model):
    _name = "scalegds5.assessment"
    _description = "Evaluación del GDS-5 del residente"
    _order = 'date desc'

    resident_id = fields.Many2one("resident", string="Residente", required=True)
    residence_id =  fields.Many2one(
        string="Residencia",
        related='resident_id.residence_id', 
        readonly=True
    )
    question_answers = fields.One2many(
        "scalegds5.answer", "assessment_id", string="Respuestas"
    )
    total_score = fields.Integer(
        string="Puntuación", compute="_compute_total_score", store=True
    )
    total_questions = fields.Integer(
        string="Cantidad de preguntas", compute="_compute_total_questions", store=True
    )
    scalegds5_state_id = fields.Many2one(
        "scalegds5.state",
        string="Estado de ánimo",
        compute="_compute_scalegds5_state",
        ondelete="restrict",
        store=True,
    )
    user_id = fields.Many2one(
        "res.users",
        string="Registrado por",
        default=lambda self: self.env.user,
        required=True,
        ondelete="restrict",
    )
    scalegds5_state_display = fields.Char(
        string="Estado de ánimo",
        compute="_compute_scalegds5_state_display",
        index=True,
        store=True,
    )
    clinic_note = fields.Text(string="Nota clínica")
    date = fields.Datetime(
        string='Fecha/Hora', 
        default=fields.Datetime.now,
        required=True
    )

    @api.depends("question_answers")
    def _compute_total_questions(self):
        for asses in self:
            asses.total_questions = len(asses.question_answers)

    @api.depends("question_answers")
    def _compute_total_score(self):
        for asses in self:
            asses.total_score = sum(
                answer.question_value
                for answer in asses.question_answers
                if answer.answer_select == answer.question_id.depression_answer
            )

    @api.depends("total_score", "question_answers")
    def _compute_scalegds5_state(self):
        ScaleGDS5State = self.env["scalegds5.state"].sudo()
        for asses in self:
            state = ScaleGDS5State.search(
                [
                    ("min_score", "<=", asses.total_score),
                    ("max_score", ">=", asses.total_score),
                ],
                limit=1,
            )
            asses.scalegds5_state_id = state[0] if state else None

    @api.depends("scalegds5_state_id")
    def _compute_scalegds5_state_display(self):
        for asses in self:
            asses.scalegds5_state_display = (
                asses.scalegds5_state_id.name
                if asses.scalegds5_state_id
                else "Fuera de la escala evaluable"
            )

    @api.depends("resident_id", "create_date")
    def _compute_display_name(self):
        for r in self:
            r.display_name = f"Evaluación de GDS-5 de {r.resident_id.name} realizada {r.create_date.strftime('%Y-%m-%d %H:%M')}"

    @api.model
    def create(self, values):
        records = super().create(values)
        # Crear log de auditoría para cada registro creado
        for record in records:
            self.env['audit.log'].sudo().crud_audit_log(record, 'scalegds5.assessment', 'create')
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
            self.env['audit.log'].sudo().crud_audit_log(record, 'scalegds5.assessment', 'write', extra_details=details)
        return result

    def unlink(self):
        # Antes de eliminar, crear logs para cada registro
        for record in self:
            self.env['audit.log'].sudo().crud_audit_log(record, 'scalegds5.assessment', 'unlink')
        return super().unlink()