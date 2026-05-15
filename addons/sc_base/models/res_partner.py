# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'
 
    municipality_id = fields.Many2one(
        "res_municipality_mx",
        string="Municipio",
        ondelete="cascade",
        required=False,
    )
    province_id = fields.Many2one(
        "res_province_mx",
        string="Estado",
        ondelete="cascade",
        required=False,
    )
    street3 = fields.Char(string='Entre Calle #2')
    street_number = fields.Char(string='Número')
    contact_address = fields.Char(
        string='Dirección Completa',
        compute='_compute_full_address',
        store=True,
    ) 

    @api.depends('street', 'street2', 'street3', 'street_number', 'city', 'province_id', 'municipality_id')
    def _compute_full_address(self):
        for record in self:
            address_complete = ''
            if record.street:
               address_complete = f"Calle {record.street}. "
            if record.street2 and record.street3:
               address_complete += f"Entre {record.street2} y {record.street2}. "
            if record.street_number:
               address_complete += f"Número {record.street_number}. "
            if record.city:
               address_complete += f"Ciudad {record.city}. "
            if record.municipality_id:
               address_complete += f"Municipio {record.municipality_id.name}. "
            if record.province_id:
               address_complete += f"Estado {record.province_id.name}."
            
            record.contact_address = address_complete
    @api.model
    def create(self, values):
        records = super().create(values)
        # Crear log de auditoría para cada registro creado
        for record in records:
            self.env['audit.log'].sudo().crud_audit_log(record, 'res.partner', 'create')
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
            self.env['audit.log'].sudo().crud_audit_log(record, 'res.partner', 'write', extra_details=details)
        return result

    def unlink(self):
        # Antes de eliminar, crear logs para cada registro
        for record in self:
            self.env['audit.log'].sudo().crud_audit_log(record, 'res.partner', 'unlink')
        return super().unlink()