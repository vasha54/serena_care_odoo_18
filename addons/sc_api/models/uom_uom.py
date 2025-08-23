import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class UoMUoM(models.Model):
    _inherit  = 'uom.uom'

    category = fields.Json(
        string="Category Datos",
        compute="_compute_category_data",
        store=False,
    )
    
    def _compute_category_data(self):
        for record in self:
            record.category = record.category_id.read(
                [
                    "id",
                    "name",
                ]
            )[0]