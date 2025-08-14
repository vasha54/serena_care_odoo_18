from odoo import models, fields, api
from odoo.exceptions import ValidationError

class AuthLevel(models.Model):
    _name = 'auth.level'
    _description = 'Nivel de autorización'
    
    name = fields.Char(string="Nivel de autorización", required=True)
    name_lower = fields.Char(
        string="Nombre en minúsculas",
        compute="_compute_name_lower",
        store=True,
        index=True
    )
    
    @api.depends("name")
    def _compute_name_lower(self):
        for record in self:
            record.name_lower = record.name.lower() if record.name else False

    _sql_constraints = [
        ("unique_name_auth_level_insensitive", 
         "UNIQUE(name_lower)", 
         "¡Ya existe un nivel de autorización con este nombre (no se distingue mayúsculas/minúsculas)!")
    ]
    
    @api.constrains("name")
    def _check_unique_name_insensitive(self):
        for record in self:
            if record.name:
                existing = self.search([
                    ("name_lower", "=", record.name.lower()),
                    ("id", "!=", record.id)
                ], limit=1)
                if existing:
                    raise ValidationError(
                        "¡Ya existe un nivel de autorización con este nombre "
                        "(no se distingue mayúsculas/minúsculas)!"
                    )