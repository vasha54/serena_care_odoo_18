from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class FamilyKinship(models.Model):
    _name = 'family.kinship'
    _description = 'Relación de parentesco familiar'
    _order = 'name'
    _rec_name = 'name'

    name = fields.Char(
        string='Parentesco',
        required=True,
        index=True,
        help='Nombre de la relación de parentesco (por ejemplo, Padre, Madre)'
    )
    description = fields.Text(
        string='Descripción',
        help='Explicación detallada de la relación'
    )
    inverse_relation = fields.Char(
        string='Relación inversa',
        help='La relación opuesta (por ejemplo, Hijo por Padre)'
    )
    degree = fields.Selection(
        [('direct', 'Directa'),
         ('extended', 'Extendida'),
         ('in_law', 'Consuegro'),
         ('other', 'Otro')],
        string='Grado de parentesco',
        default='direct'
    )

    _sql_constraints = [
        ('name_uniq_kinship', 'UNIQUE (name)', 
         '¡Ya existe un parentesco con este nombre!'),
    ]

    @api.model
    def create(self, vals_list):
        # Normalizar: si es un solo dict, convertirlo a lista
        if not isinstance(vals_list, list):
            vals_list = [vals_list]
        
        for vals in vals_list:
            if 'name' in vals:
                vals['name'] = vals['name'].strip().lower()
        
        records = super().create(vals_list)
        
        for record in records:
            self.env['audit.log'].sudo().crud_audit_log(record, 'family.kinship', 'create')
        
        return records

    def write(self, vals):
        if 'name' in vals:
            vals['name'] = vals['name'].strip().lower()
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
            self.env['audit.log'].sudo().crud_audit_log(record, 'family.kinship', 'write', extra_details=details)
        return result
    
    def unlink(self):
        # Antes de eliminar, crear logs para cada registro
        for record in self:
            self.env['audit.log'].sudo().crud_audit_log(record, 'family.kinship', 'unlink')
        return super().unlink()

    @api.constrains('name')
    def _check_name(self):
        for rec in self:
            existing = self.search([
                ('name', '=', rec.name.lower()),  # comparar en minúsculas
                ('id', '!=', rec.id)
            ], limit=1)
            if existing:
                raise ValidationError(
                    f"¡Ya existe una relación de parentesco llamada '{rec.name}'!"
                )