import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class Resident(models.Model):
    _inherit  = 'resident'

    norton_assessment_ids = fields.One2many(
        'norton.assessment', 
        'resident_id',
        string='Evaluaciones Norton',
        help="Listado de las evaluaciones Norton del residente"
    )
    scalefrail_assessment_ids = fields.One2many(
        'scalefrail.assessment', 
        'resident_id',
        string='Evaluaciones FRAIL',
        help="Listado de las evaluaciones FRAIL del residente"
    )
    scalegds5_assessment_ids = fields.One2many(
        'scalegds5.assessment', 
        'resident_id',
        string='Evaluaciones GDS-5',
        help="Listado de las evaluaciones GDS-5 del residente"
    )
    scalesarcf_assessment_ids = fields.One2many(
        'scalesarcf.assessment',
        'resident_id',
        string='Evaluaciones SARCF-5',
        help="Listado de las evaluaciones GDS-5 del residente"
    )
    barthel_assessment_ids = fields.One2many(
        'barthel.assessment',
        'resident_id',
        string='Evaluaciones Barthel',
        help="Listado de las evaluaciones Barthel del residente"
    )
    lawtonbrody_assessment_ids = fields.One2many(
        'lawtonbrody.assessment',
        'resident_id',
        string='Evaluaciones Lawton-Brody',
        help="Listado de las evaluaciones Lawton-Brody del residente"
    )