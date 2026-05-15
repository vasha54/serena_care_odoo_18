import logging
import re
import os
import base64
from dateutil.relativedelta import relativedelta
from datetime import date

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)

class RecreationalActivity(models.Model):
    _name = 'recreational.activity'
    _order = 'date_execution desc'

    date_execution = fields.Datetime(string='Fecha de realización', required=True,)
    activity_type_id = fields.Many2one(
            'nomenclature.activity.type', 
            string='Tipo de actividad', 
            ondelete='restrict',
            required=True,
    )
    description = fields.Text(
            string="Descripción", 
            required=True,
    )
    user_id = fields.Many2one(
        'res.users', 
        string='Registrado por', 
        default=lambda self: self.env.user,
        required=True,
        ondelete='restrict',
    )
    residents_ids = fields.One2many(
        'resident.recreation.activity.rel', 
        'activity_id',
        string='Residentes',
        help="Listado de los residentes que participaron",
    )
    residents = fields.One2many(
        'resident',
        compute='_compute_residents',
        string='Residentes',
        store=False,
    )
    residents_str = fields.Char(
        compute='_compute_residents',
        string='Residentes',
        store=True,
    )

    @api.depends('date_execution', 'activity_type_id')
    def _compute_display_name(self):
        for r in self:
            r.display_name = f" Actividad de Tipo {r.activity_type_id.name} - Realizada {r.date_execution.strftime("%d/%m/%Y- %H:%M:%S")}"

    
    @api.depends('residents_ids')
    def _compute_residents(self):
        for record in self:
            ids = []
            names = []
            for r in record.residents_ids:
                names.append(r.resident_id.name)
                ids.append(r.resident_id.id)
            domain = [('id', 'in', ids)]
            record.residents_str = ", ".join(names)
            record.residents = self.env['resident'].sudo().search(domain=domain)
            
    def _convert_to_iso(self, odoo_datetime):
        """Convierte datetime de Odoo a string ISO 8601"""
        if not odoo_datetime:
            return None

        # Si es un string (formato Odoo), convertir primero a objeto datetime
        if isinstance(odoo_datetime, str):
            dt_obj = fields.Datetime.from_string(odoo_datetime)
        else:  # Ya es un objeto datetime
            dt_obj = odoo_datetime

        return dt_obj.isoformat() + "Z"  # Añadir 'Z' para indicar UTC

    @api.model
    def create(self, values):
        records = super().create(values)
        # Crear log de auditoría para cada registro creado
        for record in records:
            self.env['audit.log'].sudo().crud_audit_log(record, 'recreational.activity', 'create')
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
            self.env['audit.log'].sudo().crud_audit_log(record, 'recreational.activity', 'write', extra_details=details)
        return result

    def unlink(self):
        # Antes de eliminar, crear logs para cada registro
        for record in self:
            self.env['audit.log'].sudo().crud_audit_log(record, 'recreational.activity', 'unlink')
        return super().unlink()
                

                