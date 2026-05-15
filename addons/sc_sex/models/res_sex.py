from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class ResSex(models.Model):
    _name = 'res.sex'
    _description = 'Sexo'
    _order = 'name asc'

    name = fields.Char(
        string='Nombre',
        required=True,
        index=True,
        help="Nombre completo del sexo (ej: Masculino, Femenino)")

    acronym = fields.Char(
        string='Abreviatura',
        required=True,
        size=5,
        help="Abreviatura en mayúsculas (ej: M, F)")

    _sql_constraints = [
        ('acronym_sex_unique', 'UNIQUE(acronym)', 'La abreviatura debe ser única!'),
    ]

    @api.model
    def create(self, vals_list):
        # Normalizar: si es un solo dict, convertirlo a lista
        if not isinstance(vals_list, list):
            vals_list = [vals_list]
        
        for vals in vals_list:
            _logger.info(f"Procesando: {vals}")
            # Validar nombre (asegurar que exista 'name')
            if 'name' in vals:
                self._valid_name(vals['name'])
            # Normalizar abreviatura si está presente
            if 'acronym' in vals:
                vals['acronym'] = self._normalizar_acronym(vals['acronym'])
        
        # Llamar a super() con la lista (crea múltiples registros si es necesario)
        records = super().create(vals_list)
        
        # Auditoría para cada registro creado
        for record in records:
            self.env['audit.log'].sudo().crud_audit_log(record, 'res.sex', 'create')
        
        # Devolver el recordset (si era un solo dict, será un registro único; si era lista, múltiples)
        return records

    def write(self, vals):
        if 'name' in vals:
            self._valid_name(vals['name'])
        if 'acronym' in vals:
            vals['acronym'] = self._normalizar_acronym(vals['acronym'])
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
                        changed_fields.append(
                            f"{field}: {old_val!r} -> {record[field]!r}")
                else:
                    # Campo no almacenado o no presente en el registro anterior, se registra igual
                    changed_fields.append(f"{field}: {record[field]!r}")
            if changed_fields:
                details = "Campos modificados: " + "; ".join(changed_fields)
            else:
                details = "Modificación sin cambios detectados"
            self.env['audit.log'].sudo().crud_audit_log(
                record, 'uom.uom', 'write', extra_details=details)
        return result

    def unlink(self):
        # Antes de eliminar, crear logs para cada registro
        for record in self:
            self.env['audit.log'].sudo().crud_audit_log(
                record, 'res.sex', 'unlink')
        return super().unlink()

    def _normalizar_acronym(self, abrev):
        """Convierte la abreviatura a mayúsculas y elimina espacios"""
        if abrev:
            return abrev.strip().upper()
        return abrev

    def _valid_name(self, nombre):
        """Valida que el nombre sea único (case-insensitive)"""
        if not nombre:
            return
        
        nombre_normalizado = nombre.strip().lower()
        
        # Buscar cualquier registro con el mismo nombre (ignorando mayúsculas)
        # En creación, self es el modelo, así que no hay 'id' que excluir
        Domain = [('name', '=ilike', nombre_normalizado)]
        # Si estamos en escritura (self es un recordset), excluir el registro actual
        if self and hasattr(self, 'id') and self.id:
            Domain.append(('id', '!=', self.id))
        
        existente = self.env['res.sex'].search(Domain, limit=1)
        
        if existente:
            raise ValidationError(_(
                "Ya existe un sexo con el nombre '%s' (ignorando mayúsculas/minúsculas).",
                nombre_normalizado
            ))

    @api.constrains('name')
    def _check_name_unique(self):
        for record in self:
            record._valid_name(record.name)

    @api.constrains('acronym')
    def _check_acronym(self):
        for record in self:
            if not record.acronym.isupper():
                raise ValidationError(_(
                    "La abreviatura debe estar en MAYÚSCULAS: %s",
                    record.acronym
                ))
