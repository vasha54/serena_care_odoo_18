from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError

import logging

_logger = logging.getLogger(__name__)


class ResGroups(models.Model):
    _inherit = ["res.groups"]

    # can_delete = fields.Boolean(string="Se puede eliminar", default=True)

    def unlink(self):
        for record in self:
            if record.users:
                raise UserError(
                    _(
                        "Este rol no puede eliminarse porque está "
                        "asignado a usuarios activos."
                    )
                )
            # if record.can_delete:
            #     raise UserError(
            #         _("Este Rol no puede eliminarse por ser base del sistema")
            #     )
        return super().unlink()
