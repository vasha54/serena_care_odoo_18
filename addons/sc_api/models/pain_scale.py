from odoo import models, fields, api

class PainScale(models.Model):
    _inherit = 'pain.scale'
    
    user = fields.Json(
        string="Usuario Datos",
        compute="_compute_user_data",
        store=False,
    )
    resident = fields.Json(
        string="Residente Datos",
        compute="_compute_resident_data",
        store=False,
    )

    def _compute_user_data(self):
        for record in self:
            record.user = record.user_id.read(
                [
                    "id",
                    "name",
                ]
            )[0]

    def _compute_resident_data(self):
        for record in self:
            record.resident = record.resident_id.read(
                [
                    "id",
                    "name",
                ]
            )[0] 
