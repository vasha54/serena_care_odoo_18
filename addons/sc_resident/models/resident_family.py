import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class ResidentFamily(models.Model):
    _name = 'resident.family'
    _description = 'Resident Family Model'
    _inherit  = ['soft.delete.mixin']
    _inherits = {'res.partner': 'partner_id'}

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Contacto',
        required=True,
        ondelete='cascade'
    )
    resident_ids = fields.One2many(
        'relationship.resident.family', 
        'family_id',
        string='Residentes',
    )
   
