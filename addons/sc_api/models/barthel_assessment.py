import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class BarthelAssessment(models.Model):
    _inherit = "barthel.assessment"

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
            record.question_answers_json = record.question_answers.read(
                [
                    "question_name",
                    "choise_select_name",
                    "choise_select_value",
                ]
            )
