import logging
import re

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)

class WaterBalanceAnnotation(models.Model):
    _name = 'water.balance.annotation'
    _description = 'Anotación de un ingreso/egreso de liquido de un residente'
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
    user_id = fields.Many2one(
        'res.users', 
        string='Registrado por', 
        default=lambda self: self.env.user,
        required=True,
        ondelete='restrict',
    )
    route_id = fields.Many2one(
        'water.balance.route',
        string='Vía de Ingreso/Egreso',
        required=True,
        ondelete='restrict', 
    )
    type_annotation = fields.Selection([
            ('income', 'Ingreso'),
            ('expense', 'Egreso')
        ], 
        string='Tipo', 
        required=True
    )
    quantity = fields.Float(string='Cantidad (ml)', digits=(3,1), required=True)
    notes = fields.Text(string='Observaciones')
    date = fields.Datetime(
        string='Fecha/Hora', 
        default=fields.Datetime.now,
        required=True
    )
    
    @api.depends('resident_id','user_id')
    def _compute_display_name(self):
        selection_dict = dict(self._fields["type_annotation"].selection
                    )
        for r in self:
            type_label = selection_dict.get(r.type_annotation, "")
            r.display_name = f"Registro de {type_label} de líquido de {r.resident_id.name}"
    
    @api.model
    def create(self, vals_list):
        record = super().create(vals_list)
        for r in record:
            self.env['audit.log'].sudo().crud_audit_log(r, 'water.balance.annotation', 'create')
        return record
    
    def unlink(self):
        for r in self:
            self.env['audit.log'].sudo().crud_audit_log(r, 'water.balance.annotation', 'unlink')
        return super().unlink()
    
    def write(self, vals):
        
        old_values = {}
        for record in self:
            old_values[record.id] = {
                field: record[field] for field in vals if field in record._fields and not record._fields[field].compute
            }
        result = super().write(vals)
        # Registrar auditoría con detalles de cambios
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
            self.env['audit.log'].sudo().crud_audit_log(record, 'water.balance.annotation', 'write', extra_details=details)
        return result