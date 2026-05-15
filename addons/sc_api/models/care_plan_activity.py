import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)

class CarePlanActivity(models.Model):
    _inherit = 'care.plan.activity'

    dependency_level = fields.Json(
        string="Nivel de dependencia",
        compute="_compute_dependency_level_data",
        store=False,
    )
    activity_type = fields.Json(
        string="Tipo de actividad",
        compute="_compute_activity_type_data",
        store=False,
    )
    goal = fields.Json(
        string="Objetivos",
        compute="_compute_goal_data",
        store=False,
    )
    action = fields.Json(
        string="Acciones",
        compute="_compute_action_data",
        store=False,
    )
    observation = fields.Json(
        string="Observaciones",
        compute="_compute_observation_data",
        store=False,
    )
    result = fields.Json(
        string="Resultados",
        compute="_compute_result_data",
        store=False,
    ) 

    def _compute_dependency_level_data(self):
        for record in self: 
            record.dependency_level = record.dependency_level_id.read(
                [
                    "id",
                    "name",
                ]
            )[0]

    def _compute_activity_type_data(self):
        for record in self:
            record.activity_type = record.activity_id.read(
                [
                    "id",
                    "name",
                ]
            )[0]

    def _compute_goal_data(self):
        for record in self:
            record.goal = record.goal_ids.read(
                [
                    "id",
                    "name",
                ]
            ) 

    def _compute_action_data(self):
        for record in self:
            record.action = record.action_ids.read(
                [
                    "id",
                    "name",
                ]
            )

    def _compute_observation_data(self):
        for record in self:
            record.observation = record.observation_ids.read(
                [
                    "id",
                    "name",
                ]
            ) 

    def _compute_result_data(self):
        for record in self:
            record.result = record.result_ids.read(
                [
                    "id",
                    "name",
                ]
            )


