import logging
import re
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied
from odoo import SUPERUSER_ID
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = "res.users"

    # Campo computado para obtener solo los grupos de la categoría Serena
    serena_group_ids = fields.Many2many(
        "res.groups",
        compute="_compute_serena_groups",
        inverse="_inverse_serena_groups",
        string="Grupos Serena",
        store=False,  # No se almacena directamente, es un campo virtual
    )

    @api.depends("groups_id")
    def _compute_serena_groups(self):
        """Calcula los grupos de Serena asignados al usuario"""
        serena_category = self.env.ref("sc_group.module_category_serena", False)
        if serena_category:
            # Obtener todos los grupos de la categoría Serena
            serena_groups = self.env["res.groups"].search(
                [("category_id", "=", serena_category.id)]
            )
            for user in self:
                # Filtrar solo los grupos de Serena que el usuario tiene
                user.serena_group_ids = user.groups_id & serena_groups

    def _inverse_serena_groups(self):
        """Actualiza groups_id cuando cambia serena_group_ids"""
        serena_category = self.env.ref("serena_security.module_category_serena", False)
        if serena_category:
            serena_groups = self.env["res.groups"].search(
                [("category_id", "=", serena_category.id)]
            )
            for user in self:
                # Obtener grupos actuales que NO son de Serena
                non_serena_groups = user.groups_id - serena_groups
                # Combinar con los nuevos grupos de Serena
                user.groups_id = non_serena_groups + user.serena_group_ids

    @api.model
    def _get_home_action(self):
        # # Redirigir al dashboard personalizado
        # action = self.env.ref('sc_suite.action_serena_care_dashboard', raise_if_not_found=False)
        # if action:
        #     return action.read()[0]
        return super()._get_home_action()
