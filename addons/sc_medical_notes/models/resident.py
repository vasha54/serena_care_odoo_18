import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class Resident(models.Model):
    _inherit  = 'resident'

    medical_notes_ids = fields.One2many(
        'medical.note', 
        'resident_id',
        string='Notas médicas',
        help="Listado de las anotaciones médicas realizadas vinculadas al residente"
    )
