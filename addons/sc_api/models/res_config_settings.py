# models/res_config_settings.py
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    jwt_token_expiration_value = fields.Integer(
        string='Valor de vencimiento del token JWT',
        default=12,
        config_parameter='jwt_token.expiration_value',
        help='Valor para la expiración del token JWT'
    )
    
    jwt_token_expiration_unit = fields.Selection(
        [('hours', 'Horas'), ('minutes', 'Minutos'),  ('days', 'Días')],
        string='Unidad de tiempo de vencimiento del token JWT',
        default='hours',
        config_parameter='jwt_token.expiration_unit',
        help='Unidad de tiempo de expiración (horas, minutos y horas)'
    )
    
    @api.constrains('jwt_token_expiration_value')
    def _check_jwt_token_expiration_value(self):
        for record in self:
            if record.jwt_token_expiration_value <= 0:
                raise ValidationError(_("El valor de vencimiento del token JWT debe ser mayor que 0"))