import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class ScaleSARCFAssessment(models.Model):
    _inherit = "scalesarcf.assessment"

    user = fields.Json(
        string="Usuario Datos",
        compute="_compute_user_data",
        store=False,
    )
    resident = fields.Json(
        string="Residente Datos",
        compute="_compute_resident_data",
        store=False,
    )
    question_answers_json = fields.Json(
        string="Datos de las respuestas",
        compute="_compute_question_answers_data",
        store=False,
    )

    def _compute_user_data(self):
        for record in self:
            record.user = record.user_id.read(
                [
                    "id",
                    "name",
                ]
            )[0]

    def _compute_resident_data(self):
        for record in self:
            record.resident = record.resident_id.read(
                [
                    "id",
                    "name",
                ]
            )[0]

    def _compute_question_answers_data(self):
        for record in self:
            answers_data = []
            for answer in record.question_answers:
                # Obtener la etiqueta del campo selection
                field = answer._fields["answer_select"]
                label = dict(field.get_description(answer.env)["selection"]).get(
                    answer.answer_select, answer.answer_select
                )

                answers_data.append(
                    {
                        "question_statement": answer.question_statement,
                        "answer_select": label,  # Usa la etiqueta en lugar del valor
                    }
                )
            record.question_answers_json = answers_data

    def _compute_question_answers_data(self):
        for record in self:
            record.question_answers_json = record.question_answers.read(
                [
                    "question_statement",
                    "choise_select_name",
                    "choise_select_value",
                ]
            )
