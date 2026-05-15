import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class Resident(models.Model):

    _inherit  = 'resident'

    pain_scale_ids = fields.One2many(
        'pain.scale', 
        'resident_id',
        string='Dolor',
        help="Listado de los chequeos del dolor vinculadas al residente"
    )
