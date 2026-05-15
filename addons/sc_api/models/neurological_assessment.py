from odoo import models, fields, api

class NeurologicalAssessment(models.Model):
    _inherit = 'neurological.assessment'
    
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
    neurological_state = fields.Json(
        string="Estado neurológico",
        compute="_compute_neurological_state_data",
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

    def _compute_neurological_state_data(self):
        for record in self:
            record.neurological_state = record.neurological_state_id.read(
                [
                    "id",
                    "name",
                    "color",
                    "acronym",
                    "description",
                ]
            )[0] 
    