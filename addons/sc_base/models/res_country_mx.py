import re

from odoo import api, fields, models


class ResCountryMX(models.Model):
    _name = "res_country_mx"
    _description = (
        "Modelo que representa las diferentes formas de organización del territorio en Mexico"
    )
    _inherit = ["res.country.state"]

    slug = fields.Char(
        string="Slug", compute="_compute_slug", readonly=True, store=True
    )

    @api.model
    def _get_default_country_mx(self):
        country = self.env["res.country"].search([("code", "=", "MX")], limit=1)
        return country

    country_id = fields.Many2one(
        "res.country", string="Country", default=_get_default_country_mx
    )

    @api.depends("name")
    def _compute_slug(self):
        for record in self:
            record.slug = self._generate_slug(record.name)

    def _generate_slug(self, name):
        cleaned = re.sub(r"[^\w\-]+", "", str(name))
        slug = cleaned.replace(" ", "-")
        return slug.lower()

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, f"{record.name}"))
        return result
