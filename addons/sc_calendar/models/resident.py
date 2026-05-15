import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class Resident(models.Model):
    _inherit  = 'resident'

    calendar_notes_ids = fields.One2many(
        'calendar.note', 
        'resident_id',
        string='Notas calendariadas',
        help="Listado de las anotaciones realizadas vinculadas al residente"
    )
