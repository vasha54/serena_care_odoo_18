import re
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError

import logging
_logger = logging.getLogger(__name__)

class NortonAssessment(models.Model):
    _name = 'norton.assessment'
    _description = 'Evaluación Geriátrica Norton'
    _order = 'date desc'

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
    user_id = fields.Many2one(
        'res.users', 
        string='Registrado por', 
        default=lambda self: self.env.user,
        required=True,
        ondelete='restrict',
    )
    physical_condition = fields.Selection([
        ('4', '4: Bueno'),
        ('3', '3: Regular'),
        ('2', '2: Malo'),
        ('1', '1: Muy Malo'),
    ], string='Estado Físico', required=True)
    
    mental_state = fields.Selection([
        ('4', '4: Alerta'),
        ('3', '3: Apático'),
        ('2', '2: Confuso'),
        ('1', '1: Estuporoso'),
    ], string='Estado Mental', required=True)
    
    activity = fields.Selection([
        ('4', '4: Deambula normalmente'),
        ('3', '3: Camina con ayuda'),
        ('2', '2: Se sienta, no camina'),
        ('1', '1: Postrado en cama'),
    ], string='Actividad', required=True)
    
    mobility = fields.Selection([
        ('4', '4: Total'),
        ('3', '3: Ligera limitación'),
        ('2', '2: Muy limitado'),
        ('1', '1: Inmóvil'),
    ], string='Movilidad', required=True)
    
    incontinence = fields.Selection([
        ('4', '4: Ninguna'),
        ('3', '3: Ocasional'),
        ('2', '2: Urinaria'),
        ('1', '1: Urinaria y fecal'),
    ], string='Incontinencia', required=True)
    
    # Campos calculados
    total_score = fields.Integer(
        string='Puntuación Total',
        compute='_compute_total_score',
        store=True
    )
    
    risk_level = fields.Selection([
        ('low', 'Sin riesgo o riesgo mínimo (16-20)'),
        ('medium', 'Riesgo medio o potencial (13-15)'),
        ('high', 'Riesgo alto de úlceras por presión (0-12)'),
    ], string='Nivel de Riesgo', compute='_compute_risk_level', store=True) 

    @api.depends('physical_condition', 'mental_state', 'activity', 'mobility', 'incontinence')
    def _compute_total_score(self):
        for record in self:
            total = 0
            total += int(record.physical_condition) if record.physical_condition else 0
            total += int(record.mental_state) if record.mental_state else 0
            total += int(record.activity) if record.activity else 0
            total += int(record.mobility) if record.mobility else 0
            total += int(record.incontinence) if record.incontinence else 0
            record.total_score = total
    
    @api.depends('total_score')
    def _compute_risk_level(self):
        for record in self:
            score = record.total_score
            if score >= 16:
                record.risk_level = 'low'
            elif score > 12 and score <= 15:
                record.risk_level = 'medium'
            elif score <= 12:
                record.risk_level = 'high'

    @api.depends('resident_id')
    def _compute_display_name(self):
        for r in self:
            r.display_name = f"Evaluación Norton de {r.resident_id.name}"
            
    @api.model
    def create(self, values):
        records = super().create(values)
        # Crear log de auditoría para cada registro creado
        for record in records:
            self.env['audit.log'].sudo().crud_audit_log(record, 'norton.assessment', 'create')
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
            self.env['audit.log'].sudo().crud_audit_log(record, 'norton.assessment', 'write', extra_details=details)
        return result

    def unlink(self):
        # Antes de eliminar, crear logs para cada registro
        for record in self:
            self.env['audit.log'].sudo().crud_audit_log(record, 'norton.assessment', 'unlink')
        return super().unlink()
           