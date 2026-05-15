# -*- coding: utf-8 -*-

import logging
import json


from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class OperationInventory(models.Model):
    _inherit  = 'operation.inventory'

    def export_xlsx(self):
        active_ids = self.env.context.get("active_ids", [])
        active_domain = self.env.context.get("search_domain", [])

        if active_ids:
            record_ids = active_ids
        else:
            record_ids = self.search(active_domain).ids

        return {
            "type": "ir.actions.act_url",
            "url": "/operation_inventory/excel_report/%s" % json.dumps(record_ids),
            "target": "new",
        }