from odoo import models, fields, api

class Hygiene(models.Model):
    _inherit = 'hygiene'
    
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
    htype = fields.Json(
        string="Tipo de Higiene Datos",
        compute="_compute_type_data",
        store=False,
    )
    etype = fields.Json(
        string="Tipo de Evacuación Datos",
        compute="_compute_type_evacuation_data",
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

    def _compute_type_data(self):
        for record in self:
            record.htype = record.hygiene_type_id.read(
                [
                    "id",
                    "name",
                ]
            )[0]

    def _compute_type_evacuation_data(self):
        for record in self:
            if record.evacuation_type_id :
                record.etype = record.evacuation_type_id.read(
                    [
                        "id",
                        "name",
                    ]
                )[0]
            else:
                record.etype = False
