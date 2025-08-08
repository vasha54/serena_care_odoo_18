from odoo import models, fields


class Resident(models.Model):
    _name = 'resident'
    _description = 'Resident Model'
    _inherits = {'res.partner': 'partner_id'}

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Contacto',
        required=True,
        ondelete='cascade'
    )
    sex_id = fields.Many2one(
        comodel_name='res.sex',
        string='Sexo',
        required=True,
        help='Sexo a la que pertenece el residente',
    )
    residence_id = fields.Many2one(
        comodel_name='residence_house',
        string='Residencia',
        required=True,
        help='Residencia a la que pertenece el residente',
        domain="[('active', '=', True)]"
    )
    birth_date = fields.Date(
        string='Fecha de Nacimiento',
        required=True,
        help='Fecha de nacimiento del residente'
    )
    country_id = fields.Many2one(
        comodel_name='res.country',
        string='País',
        default=lambda self: self.env.ref('base.mx',False),
        help='País de origen del residente'
    )