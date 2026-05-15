import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class Resident(models.Model):
    _inherit  = 'resident'

    neurological_assessment_ids = fields.One2many(
        'neurological.assessment', 
        'resident_id',
        string='Evaluaciones neorológicas',
        help="Listado de las evaluaciones nerológicas del residente"
    )