import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class Resident(models.Model):
    _inherit = "resident"

    water_balance_ids = fields.One2many(
        "water.balance.annotation",
        "resident_id",
        string="Registros del balance hídrico",
        help="Listado del balance hídrico del residente",
    )
