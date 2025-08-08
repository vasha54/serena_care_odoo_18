import logging
import datetime
from os import unlink
import re
from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class ResidenceHouse(models.Model):
    _inherit = 'residence_house'

    employee_ids = fields.One2many(
        'hr.employee',
        'residence_id',
        string='Empleados Asignados'
    )

    employee_count = fields.Integer(
        string='Número de Empleados',
        compute='_compute_employee_count',
        store=False
    )

    @api.depends('employee_ids')
    def _compute_employee_count(self):
        for rec in self:
            rec.employee_count = len(rec.employee_ids)

    def open_reassignment_employee_wizard(self):
        return {
            'name': "Reasignar Empleados",
            'type': 'ir.actions.act_window',
            'res_model': 'reassign.employee.residence.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_current_residence_id': self.id,
            }
        }
