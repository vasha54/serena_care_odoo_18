from odoo import models, fields, api

class Nutrition(models.Model):
    _inherit = 'nutrition'
    
    user_data = fields.Json(
        string="Usuario Datos",
        compute="_compute_user_data",
        store=False,
    )
    resident_data = fields.Json(
        string="Residente Datos",
        compute="_compute_resident_data",
        store=False,
    )
    level = fields.Json(
        string="Nivel Datos",
        compute="_compute_level_data",
        store=False,
    )

    def _compute_user_data(self):
        for record in self:
            record.user_data = record.user_id.read(
                [
                    "id",
                    "name",
                ]
            )[0]

    def _compute_resident_data(self):
        for record in self:
            record.resident_data = record.resident_id.read(
                [
                    "id",
                    "name",
                ]
            )[0] 

    def _compute_level_data(self):
        for record in self:
            record.level = record.nutrition_level_id.read(
                [
                    "id",
                    "name",
                    "percent",
                ]
            )[0] 
    