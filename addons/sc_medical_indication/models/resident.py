import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)

class Resident(models.Model):
    _inherit  = 'resident'

    medical_indication_ids = fields.One2many(
        'unified.medical.indication', 
        'resident_id',
        string='Indicaciones médicas',
        help="Listado de las indicaciones médicas realizadas al residente"
    )