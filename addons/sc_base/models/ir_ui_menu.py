from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)

class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    is_ui_menu_serena = fields.Boolean(
        string="Es Menú de Serena",
        default=False,
    )

    @api.model
    def create(self, vals):
        current_context = self.env.context
        if current_context.get('ui_menu_serena'):
            vals['is_ui_menu_serena'] = True
        return super().create(vals)
