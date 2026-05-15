import re
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError

import logging
_logger = logging.getLogger(__name__)

class PainScale(models.Model):
    _name = 'pain.scale'
    _description = 'Modelo del registro de la escala del dolor'

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
    date = fields.Datetime(
        string='Fecha/Hora', 
        default=fields.Datetime.now,
        required=True
    )
    description = fields.Text(string='Descripción')
    user_id = fields.Many2one(
        'res.users', 
        string='Registrado por', 
        default=lambda self: self.env.user,
        required=True,
        ondelete='restrict',
    )
    value_pain = fields.Integer(
        string='Valor cuantitativo',
        required=True
    )
    pain_status = fields.Selection(
        string='Estado del dolor',
        selection=[
            ('no_pain', 'Sin dolor'),
            ('a_little', 'Un poco'),
            ('moderate', 'Moderado'),
            ('severe', 'Severo'),
            ('very_severe', 'Muy severo'),
            ('worst_pain', 'El peor dolor'),
        ],
        compute='_compute_pain_status',
        store=True  # Opcional: almacena el valor en la base de datos
    )
    
    @api.depends('value_pain')
    def _compute_pain_status(self):
        for record in self:
            if record.value_pain == 0:
                record.pain_status = 'no_pain'
            elif 1 <= record.value_pain <= 3:
                record.pain_status = 'a_little'
            elif 4 <= record.value_pain <= 5:
                record.pain_status = 'moderate'
            elif record.value_pain == 6:
                record.pain_status = 'severe'
            elif 7 <= record.value_pain <= 9:
                record.pain_status = 'very_severe'
            elif record.value_pain == 10:
                record.pain_status = 'worst_pain'
            else:
                record.pain_status = False

    @api.depends('resident_id')
    def _compute_display_name(self):
        for r in self:
            r.display_name = f"Escala del dolor de {r.resident_id.name}"

    @api.constrains('value_pain')
    def _check_value_pain_range(self):
        for record in self:
            if record.value_pain < 0 or record.value_pain > 10:
                raise ValidationError("El valor del dolor debe estar entre 0 y 10.")
            
    @api.model
    def create(self, values):
        records = super().create(values)
        # Crear log de auditoría para cada registro creado
        for record in records:
            self.env['audit.log'].sudo().crud_audit_log(record, 'pain.scale', 'create')
        return records

    def write(self, values):
        # Guardar estado anterior para detectar cambios (opcional, mejora la calidad del detalle)
        old_values = {}
        for record in self:
            old_values[record.id] = {
                field: record[field] for field in values if field in record._fields and not record._fields[field].compute
            }
        result = super().write(values)
        # Después de la escritura, crear logs con los campos modificados
        for record in self:
            changed_fields = []
            for field, new_val in values.items():
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
            self.env['audit.log'].sudo().crud_audit_log(record, 'pain.scale', 'write', extra_details=details)
        return result

    def unlink(self):
        # Antes de eliminar, crear logs para cada registro
        for record in self:
            self.env['audit.log'].sudo().crud_audit_log(record, 'pain.scale', 'unlink')
        return super().unlink()

