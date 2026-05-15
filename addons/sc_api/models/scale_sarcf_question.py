import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)

class ScaleSARCFQuestion(models.Model):
    _inherit = 'scalesarcf.question'

    choises = fields.Json(
        string="Opciones de Datos preguntas",
        compute="_compute_choises_data",
        store=False,
    )

    def _compute_choises_data(self):
        for record in self:
            record.choises = record.choise_ids.read(
                [
                    "id",
                    "name",
                    "value"
                ]
            )
