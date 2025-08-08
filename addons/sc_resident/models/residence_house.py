import logging
import datetime
from os import unlink
import re
from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class ResidenceHouse(models.Model):
    _inherit = 'residence_house'

    resident_ids = fields.One2many(
        'resident',
        'residence_id',
        string='Residentes'
    )

    resident_count = fields.Integer(
        string='Número de Residentes',
        compute='_compute_resident_count',
        store=False
    )

    @api.depends('resident_ids')
    def _compute_resident_count(self):
        for rec in self:
            rec.resident_count = len(rec.resident_ids)

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
