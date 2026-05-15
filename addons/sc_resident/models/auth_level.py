from odoo import models, fields, api
from odoo.exceptions import ValidationError

class AuthLevel(models.Model):
    _name = 'auth.level'
    _description = 'Nivel de autorización'
    
    name = fields.Char(string="Nivel de autorización", required=True)
    name_lower = fields.Char(
        string="Nombre en minúsculas",
        compute="_compute_name_lower",
        store=True,
        index=True
    )
    
    @api.depends("name")
    def _compute_name_lower(self):
        for record in self:
            record.name_lower = record.name.lower() if record.name else False

    _sql_constraints = [
        ("unique_name_auth_level_insensitive", 
         "UNIQUE(name_lower)", 
         "¡Ya existe un nivel de autorización con este nombre (no se distingue mayúsculas/minúsculas)!")
    ]
    
    @api.constrains("name")
    def _check_unique_name_insensitive(self):
        for record in self:
            if record.name:
                existing = self.search([
                    ("name_lower", "=", record.name.lower()),
                    ("id", "!=", record.id)
                ], limit=1)
                if existing:
                    raise ValidationError(
                        "¡Ya existe un nivel de autorización con este nombre "
                        "(no se distingue mayúsculas/minúsculas)!"
                    )
                    
    @api.model
    def create(self, values):
        records = super().create(values)
        # Crear log de auditoría para cada registro creado
        for record in records:
            self.env['audit.log'].sudo().crud_audit_log(record, 'auth.level', 'create')
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
            self.env['audit.log'].sudo().crud_audit_log(record, 'auth.level', 'write', extra_details=details)
        return result

    def unlink(self):
        # Antes de eliminar, crear logs para cada registro
        for record in self:
            self.env['audit.log'].sudo().crud_audit_log(record, 'auth.level', 'unlink')
        return super().unlink()