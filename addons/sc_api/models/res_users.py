from odoo import api, fields, models

class ResUsers(models.Model):
    _inherit = 'res.users'

    jwt_token = fields.Char(string="JWT Token", copy=False)
    token_expiration = fields.Datetime(string="Token Expiration", copy=False)
    contact_address = fields.Char(related='parent_id.contact_address',
                                  store=False, readonly=True)
    groups_data = fields.Json(
        string="Grupos Datos",
        compute="_compute_group_data",
        store=False,
    )
    country = fields.Json(
        string="País Datos",
        compute="_compute_country_data",
        store=False,
    )
    province = fields.Json(
        string="Provincia Datos",
        compute="_compute_province_data",
        store=False,
    )
    municipality = fields.Json(
        string="Municipios Datos",
        compute="_compute_municipality_data",
        store=False,
    )

    def _compute_country_data(self):
        for record in self:
            record.country = False
            if record.country_id:
                record.country = record.country_id.read(
                    [
                        "id",
                        "name",
                    ]
                )[0]


    def _compute_province_data(self):
        for record in self:
            record.province = False
            if record.province_id:
                record.province = record.province_id.read(
                    [
                        "id",
                        "name",
                    ]
                )[0]

    def _compute_municipality_data(self):
        for record in self:
            record.municipality = False
            if record.municipality_id:
                record.municipality = record.municipality_id.read(
                    [
                        "id",
                        "name",
                    ]
                )[0]

    def _compute_group_data(self):
        for record in self:
            record.groups_data = False
            if record.groups_id:
                record.groups_data = record.groups_id.read(
                    [
                        "id",
                        "name",
                    ]
                )

    @api.model
    def _clear_expired_tokens(self):
        """ Limpia los tokens expirados (token_expiration anterior a la fecha actual) """
        now = fields.Datetime.now()
        expired_users = self.search([
            ('token_expiration', '<', now),
            ('jwt_token', '!=', False)
        ])
        expired_users.write({
            'jwt_token': False,
            'token_expiration': False
        })
