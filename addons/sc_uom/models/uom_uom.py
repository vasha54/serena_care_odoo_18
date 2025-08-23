import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class UoMUoM(models.Model):
    _inherit  = 'uom.uom'

    is_uom_sc = fields.Boolean(help="Medición gestionada por Serena - Care", default=False)


    @api.model
    def create(self, values):
        current_context = self.env.context 
        if 'uom_sc' in current_context:
            values['is_uom_sc'] = True 
        result = super().create(values)
        return result