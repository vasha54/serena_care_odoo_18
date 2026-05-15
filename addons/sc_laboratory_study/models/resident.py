import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class Resident(models.Model):
    _inherit  = 'resident'

    laboratory_file_ids = fields.One2many(
        'laboratory.file', 
        'resident_id',
        string='Estudio de Labboratorio',
        help="Listado de de los ficheros de estudios de laboratorio realizado al paciente"
    )