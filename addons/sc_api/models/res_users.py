from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    jwt_token = fields.Char(string="JWT Token", copy=False)
    token_expiration = fields.Datetime(string="Token Expiration", copy=False)