import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class RelationshipResidentFamily(models.Model):
    _inherit = 'relationship.resident.family'

    auth_level = fields.Json(
        string="Niveles de autorización",
        compute="_compute_auth_level_data",
        store=False,
    )
    kinship = fields.Json(
        string="Residente Datos",
        compute="_compute_kinship_data",
        store=False,
    )
    family_ident = fields.Integer(string='Identificador', compute='_compute_id')

    def _compute_auth_level_data(self):
        for record in self:
            record.auth_level = record.auth_level_ids.read(
                [
                    "id",
                    "name",
                ]
            )

    def _compute_kinship_data(self):
        for record in self:
            record.kinship = record.kinship_id.read(
                [
                    "id",
                    "name",
                ]
            )[0]

    def _compute_id(self):
        for record in self:
            record.family_ident = record.family_id.id

    