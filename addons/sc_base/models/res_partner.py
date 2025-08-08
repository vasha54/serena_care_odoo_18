# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'
 
    municipality_id = fields.Many2one(
        "res_municipality_mx",
        string="Municipio",
        ondelete="cascade",
        required=False,
    )
    province_id = fields.Many2one(
        "res_province_mx",
        string="Estado",
        ondelete="cascade",
        required=False,
    )
    street3 = fields.Char(string='Entre Calle #2')
    street_number = fields.Char(string='Número')
    contact_address = fields.Char(
        string='Dirección Completa',
        compute='_compute_full_address',
        store=True,
    ) 

    @api.depends('street', 'street2', 'street3', 'street_number', 'city', 'province_id', 'municipality_id')
    def _compute_full_address(self):
        for record in self:
            address_complete = ''
            if record.street:
               address_complete = f"Calle {record.street}. "
            if record.street2 and record.street3:
               address_complete += f"Entre {record.street2} y {record.street2}. "
            if record.street_number:
               address_complete += f"Número {record.street_number}. "
            if record.city:
               address_complete += f"Ciudad {record.city}. "
            if record.municipality_id:
               address_complete += f"Municipio {record.municipality_id.name}. "
            if record.province_id:
               address_complete += f"Estado {record.province_id.name}."
            
            record.contact_address = address_complete