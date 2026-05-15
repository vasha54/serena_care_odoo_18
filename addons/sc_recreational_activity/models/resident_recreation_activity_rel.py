import logging
import re
import os
import base64
from dateutil.relativedelta import relativedelta
from datetime import date, timedelta


from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)

class ResidentRecreationalActivityRel(models.Model):
    _name = 'resident.recreation.activity.rel'
    _order = 'date_execution desc'

    resident_id = fields.Many2one(
            'resident',
            string='Residente',
            required=True,
            ondelete='restrict',
    )
    residence_id =  fields.Many2one(
        string="Residencia",
        related='resident_id.residence_id', 
        readonly=True
    )
    activity_id = fields.Many2one(
            'recreational.activity',
            string='Actividad',
            required=True,
            ondelete='restrict',
    )
    date_execution = fields.Datetime(
            related='activity_id.date_execution',
            string='Fecha de realización', 
            required=True,
    )
    activity_type_id = fields.Many2one(
            related='activity_id.activity_type_id',
            string='Tipo de actividad', 
            ondelete='restrict',
            required=True,
    )
    description = fields.Text(
            related='activity_id.description',
            string="Descripción", 
            required=True,
    )
    user_id = fields.Many2one(
        related='activity_id.user_id',
        string='Registrado por', 
        default=lambda self: self.env.user,
        required=True,
        ondelete='restrict',
    )

    _sql_constraints = [
        ('unique_resident_recreation_activity', 
         'UNIQUE(resident_id, activity_id)', 
         '¡Ya existe un registro con este residente y actividad! Solo se permite uno por combinación.')
    ]

    @api.constrains('resident_id', 'activity_id')
    def _check_unique_resident_family(self):
        for record in self:
            if not record.resident_id or not record.activity_id:
                continue
                
            domain = [
                ('resident_id', '=', record.resident_id.id),
                ('activity_id', '=', record.activity_id.id),
                ('id', '!=', record.id)
            ]
            
            if self.search_count(domain) > 0:
                raise ValidationError(_(
                    "¡Ya existe una relación entre el residente %(resident)s y la actividad '%(family)s'! "
                    "No se permiten relaciones duplicadas."
                ) % {
                    'resident': record.resident_id.name,
                    'activity': record.activity_id.description
                })
                
    @api.model
    def create(self, values):
        records = super().create(values)
        # Crear log de auditoría para cada registro creado
        for record in records:
            self.env['audit.log'].sudo().crud_audit_log(record, 'resident.recreation.activity.rel', 'create')
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
            self.env['audit.log'].sudo().crud_audit_log(record, 'resident.recreation.activity.rel', 'write', extra_details=details)
        return result

    def unlink(self):
        # Antes de eliminar, crear logs para cada registro
        for record in self:
            self.env['audit.log'].sudo().crud_audit_log(record, 'resident.recreation.activity.rel', 'unlink')
        return super().unlink()