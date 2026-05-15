import logging
import json
from dateutil.relativedelta import relativedelta
from datetime import date

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)

class RecreationalActivity(models.Model):
    _inherit  = 'recreational.activity'


    def export_xlsx(self):
        active_ids = self.env.context.get("active_ids", [])
        active_domain = self.env.context.get("search_domain", [])

        if active_ids:
            record_ids = active_ids
        else:
            record_ids = self.search(active_domain).ids

        return {
            "type": "ir.actions.act_url",
            "url": "/recreational_activity/excel_report/%s" % json.dumps(record_ids),
            "target": "new",
        }


    
                

                