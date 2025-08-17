import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class Resident(models.Model):
    _inherit  = 'resident'

    vital_signs_ids = fields.One2many(
        'vital.signs', 
        'resident_id',
        string='Signos vitales',
        help="Listado de las tomas de signos vitales que se le ha realizado el residente"
    )
