from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)

class IrUiView(models.Model):
    _inherit = 'ir.ui.view'

    is_ui_view_serena = fields.Boolean(
        string="Es Vista de Serena",
        default=False,
    )

    @api.model
    def create(self, vals):
        current_context = self.env.context
        if current_context.get('ui_view_serena'):
            vals['is_ui_view_serena'] = True
        return super().create(vals)
