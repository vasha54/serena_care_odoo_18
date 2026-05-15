import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)

class Resident(models.Model):
    _inherit = "resident"

    care_plan_id = fields.Many2one('care.plan',string="Plan de Cuidado")
    plan_activity_ids = fields.One2many(
        related='care_plan_id.plan_activity_ids', 
        string="Actividades del Plan",
        readonly=False
    )
    diagnosis_care_plan = fields.Text(
        related='care_plan_id.diagnosis',
        string="Diagnóstico del Plan",
        readonly=False
    )
    plan_care_level_id = fields.Many2one(
        related='care_plan_id.care_level_id',
        string="Nivel de Cuidado",
        required=True,
        readonly=False,
        domain=[('active','=',True)]
    )

    
