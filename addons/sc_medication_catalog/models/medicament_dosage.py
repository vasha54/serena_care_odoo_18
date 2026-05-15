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
    
    @api.model
    def create(self, values):
        records = super().create(values)
        # Crear log de auditoría para cada registro creado
        for record in records:
            self.env['audit.log'].sudo().crud_audit_log(record, 'medicament.dosage', 'create')
        return records
    
    def write(self, vals):
        # Guardar estado anterior para detectar cambios (opcional, mejora la calidad del detalle)
        old_values = {}
        for record in self:
            old_values[record.id] = {
                field: record[field] for field in vals if field in record._fields and not record._fields[field].compute
            }
        result = super().write(vals)
        # Después de la escritura, crear logs con los campos modificados
        for record in self:
            changed_fields = []
            for field, new_val in vals.items():
                if field in old_values.get(record.id, {}):
                    old_val = old_values[record.id][field]
                    if old_val != record[field]:
                        changed_fields.append(f"{field}: {old_val!r} -> {record[field]!r}")
                else:
                    # Campo no almacenado o no presente en el registro anterior, se registra igual
                    changed_fields.append(f"{field}: {record[field]!r}")
            if changed_fields:
                details = "Campos modificados: " + "; ".join(changed_fields)
            else:
                details = "Modificación sin cambios detectados"
            self.env['audit.log'].sudo().crud_audit_log(record, 'medicament.dosage', 'write', extra_details=details)
        return result

    def unlink(self):
        # Antes de eliminar, crear logs para cada registro
        for record in self:
            self.env['audit.log'].sudo().crud_audit_log(record, 'medicament.dosage', 'unlink')
        return super().unlink()