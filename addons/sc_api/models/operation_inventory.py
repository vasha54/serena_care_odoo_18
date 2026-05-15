from odoo import models, fields, api

class OperationInventory(models.Model):
    _inherit = 'operation.inventory'

    resident = fields.Json(
        string="Residente Datos",
        compute="_compute_resident_data",
        store=False,
    )
    uom = fields.Json(
        string="Unidad de Medida Datos",
        compute="_compute_uom_data",
        store=False,
    )
    medication = fields.Json(
        string="Medicamento Datos",
        compute="_compute_medication_data",
        store=False,
    )
    user = fields.Json(
        string="Usuaurio Datos",
        compute="_compute_user_data",
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

    def _compute_medication_data(self):
        for record in self:
            record.medication = record.medication_id.read(
                [
                    "id",
                    "name",
                ]
            )[0]

    def _compute_uom_data(self):
        for record in self:
            record.uom = record.uom_id.read(
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
