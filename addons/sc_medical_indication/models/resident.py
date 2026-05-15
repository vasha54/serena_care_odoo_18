import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class Resident(models.Model):
    _inherit = 'resident'

    medical_indication_ids = fields.One2many(
        'unified.medical.indication',
        'resident_id',
        string='Indicaciones médicas',
        help="Listado de las indicaciones médicas realizadas al residente"
    )

    medical_indication_general_ids = fields.One2many(
        'medical.indication',
        'resident_id',
        string='Indicaciones médicas general',
        help="Listado de las indicaciones médicas generales realizadas al residente"
    )

    medical_indication_medication_ids = fields.One2many(
        'medical.medication',
        'resident_id',
        string='Indicaciones médicas de medicamentos',
        help="Listado de las indicaciones médicas de medicamentos realizadas al residente"
    )
