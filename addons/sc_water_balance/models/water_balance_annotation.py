import logging
import re

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)

class WaterBalanceAnnotation(models.Model):
    _name = 'water.balance.annotation'
    _description = 'Anotación de un ingreso/egreso de liquido de un residente'

    resident_id = fields.Many2one(
        'resident', 
        string='Residente',
        required=True,
        ondelete='restrict',
    )
    user_id = fields.Many2one(
        'res.users', 
        string='Registrado por', 
        default=lambda self: self.env.user,
        required=True,
        ondelete='restrict',
    )
    route_id = fields.Many2one(
        'water.balance.route',
        string='Vía de Ingreso/Egreso',
        required=True,
        ondelete='restrict', 
    )
    type_annotation = fields.Selection([
            ('income', 'Ingreso'),
            ('expense', 'Egreso')
        ], 
        string='Tipo', 
        required=True
    )
    quantity = fields.Float(string='Cantidad (ml)', digits=(3,1), required=True)
    notes = fields.Text(string='Observaciones')