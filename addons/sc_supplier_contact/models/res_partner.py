# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'
 
    is_supplier_sc = fields.Boolean("Es proveedor de Serena Care", default=False)
