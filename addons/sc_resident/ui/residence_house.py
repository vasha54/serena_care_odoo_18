import logging
import datetime
from os import unlink
import re
from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class ResidenceHouse(models.Model):
    _inherit = 'residence_house'

    def open_reassignment_resident_wizard(self):
        return {
            'name': "Reasignar Residentes",
            'type': 'ir.actions.act_window',
            'res_model': 'reassign.resident.residence.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_current_residence_id': self.id,
            }
        }

