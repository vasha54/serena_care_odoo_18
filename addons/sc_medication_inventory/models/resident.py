import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class Resident(models.Model):
    _inherit = "resident"

    medication_inventory_ids = fields.One2many(
        "medication.inventory",
        "resident_id",
        string="Medicamentos",
        help="Inventario de Medicamentos del Residente",
    )
    
    
    
    
