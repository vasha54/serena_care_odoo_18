import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class Resident(models.Model):
    _inherit  = 'resident'

    nursing_notes_ids = fields.One2many(
        'nursing.note', 
        'resident_id',
        string='Notas de enfermería',
        help="Listado de las anotaciones realizadas vinculadas al residente"
    )
