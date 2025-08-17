from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

import logging
import re

_logger = logging.getLogger(__name__)


class MedicamentDosage(models.Model):
    _name = 'medicament.dosage'
    _description = 'Dosis por Grupo Poblacional'

    medicament_id = fields.Many2one(
        'medicament.product', 
        string='Medicamento',
        required=True,
        ondelete='cascade'
    )
    population_group_id = fields.Many2one(
        'population.group',
        string='Grupo Poblacional',
        required=True,
        ondelete='restrict',
    )
    route_id = fields.Many2one(
        'administration.route',
        string='Vía de Administración',
        required=True,
        ondelete='restrict', 
    )
    
    dosage = fields.Text(string='Dosis')

    # Restricción para evitar duplicados
    _sql_constraints = [
        ('unique_dosage_config', 
         'unique(medicament_id, population_group_id, route_id)', 
         '¡Ya existe una configuración para este grupo poblacional y vía de administración!')
    ]

    @api.constrains('route_id')
    def _check_route_in_use(self):
        for rec in self:
            if rec.route_id and not rec.route_id.active:
                raise ValidationError(
                    "La vía de administración %s está desactivado y no puede usarse" % rec.route_id.name
                )

    @api.constrains('population_group_id')
    def _check_population_group_in_use(self):
        for rec in self:
            if rec.population_group_id and not rec.population_group_id.active:
                raise ValidationError(
                    "El grupo poblacional %s está desactivado y no puede usarse" % rec.population_group_id.name
                )