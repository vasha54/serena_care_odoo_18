import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class Resident(models.Model):
    _inherit  = 'resident'

    anomaly_ids = fields.One2many(
        'anomaly', 
        'resident_id',
        string='Anomalías',
        help="Listado de las anomalías vinculadas al residente"
    )
