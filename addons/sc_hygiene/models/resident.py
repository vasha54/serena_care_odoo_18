import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class Resident(models.Model):
    _inherit  = 'resident'

    hygiene_ids = fields.One2many(
        'hygiene', 
        'resident_id',
        string='Higiene',
        help="Listado de registros de higiene vinculadas al residente"
    )
