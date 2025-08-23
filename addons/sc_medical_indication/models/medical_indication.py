import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)

class MedicalIndication(models.Model):
    _name = 'medical.indication'
    _description = 'Indicación Médica General'
    
    user_id = fields.Many2one(
        'res.users', 
        string='Doctor',
        default=lambda self: self.env.user,
        required=True,
        ondelete='restrict',
    )
    resident_id = fields.Many2one(
        'resident', 
        string='Residente',
        required=True,
        ondelete='restrict',
        tracking=True,
    )
    
    
    note = fields.Text(string='Indicación',tracking=True)

    def _get_tracked_fields(self):
        """Obtener todos los campos con tracking habilitado"""
        return [name for name, field in self._fields.items() if getattr(field, 'tracking', False)]

    def _format_value(self, field, value):
        """Formatear valores para mostrar en los detalles de auditoría"""
        if value is False or value is None:
            return "Vacío"
        
        field_type = self._fields[field].type
        if field_type in ['many2one', 'one2many', 'many2many']:
            if field_type == 'many2one':
                record = self.env[self._fields[field].comodel_name].browse(value)
                return record.display_name if record else str(value)
            else:
                return str(value)
        else:
            return str(value)

    @api.model
    def create(self, vals):
        # Antes de crear, verificar las residencias permitidas
        if vals.get('user_id') and vals.get('resident_id'):
            user = self.env['res.users'].browse(vals['user_id'])
            resident = self.env['resident'].browse(vals['resident_id'])
            
            # Verificar si el usuario está vinculado a un empleado
            if not user.employee_id:
                raise UserError(_('El usuario seleccionado no está asociado a un empleado.'))
            
            # Obtener residencias permitidas del empleado (asignada + alternativas)
            employee = user.employee_id
            allowed_residences = employee.alternative_residences_ids + employee.residence_id
            
            # Verificar si la residencia del residente está permitida
            if resident.residence_id not in allowed_residences:
                raise UserError(_('No tiene permisos para crear indicaciones en esta residencia.'))
        
        return super().create(vals)

    def write(self, vals):
        # Verificar autorización para cada registro
        for record in self:
            if self.env.user != record.user_id:
                # Registrar acceso denegado
                self.env['audit.log'].create({
                    'name': f"Intento de modificación no autorizado de Indicación Médica (ID: {record.id})",
                    'user_id': self.env.user.id,
                    'model_id': self.env['ir.model']._get('medical.indication').id,
                    'record_id': record.id,
                    'action_type': 'access_denied',
                    'details': f"El usuario {self.env.user.name} intentó modificar una indicación médica que pertenece al usuario {record.user_id.name}."
                })
                raise UserError(_('No está autorizado a modificar esta indicación médica.'))
        
        # Capturar valores antiguos de campos con tracking
        tracked_fields = self._get_tracked_fields()
        old_values = {}
        for record in self:
            old_values[record.id] = {}
            for field in tracked_fields:
                if field in vals:
                    old_values[record.id][field] = record[field]
        
        # Ejecutar la escritura normal
        result = super(MedicalIndication, self).write(vals)
        
        # Registrar cambios exitosos
        for record in self:
            changes = []
            for field in tracked_fields:
                if field in vals:
                    old_value = old_values[record.id].get(field)
                    new_value = record[field]
                    if old_value != new_value:
                        old_value_str = self._format_value(field, old_value)
                        new_value_str = self._format_value(field, new_value)
                        changes.append(f"{field}: {old_value_str} -> {new_value_str}")
            
            if changes:
                self.env['audit.log'].create({
                    'name': f"Modificación de Indicación Médica (ID: {record.id})",
                    'user_id': self.env.user.id,
                    'model_id': self.env['ir.model']._get('medical.indication').id,
                    'record_id': record.id,
                    'action_type': 'write',
                    'details': '\n'.join(changes)
                })
        
        return result

    def unlink(self):
        # Verificar autorización para cada registro
        for record in self:
            if self.env.user != record.user_id:
                # Registrar acceso denegado
                self.env['audit.log'].create({
                    'name': f"Intento de eliminación no autorizado de Indicación Médica (ID: {record.id})",
                    'user_id': self.env.user.id,
                    'model_id': self.env['ir.model']._get('medical.indication').id,
                    'record_id': record.id,
                    'action_type': 'access_denied',
                    'details': f"El usuario {self.env.user.name} intentó eliminar una indicación médica que pertenece al usuario {record.user_id.name}."
                })
                raise UserError(_('No está autorizado a eliminar esta indicación médica.'))
            
            # Registrar eliminación exitosa
            self.env['audit.log'].sudo().create({
                'name': f"Eliminación de Indicación Médica (ID: {record.id})",
                'user_id': self.env.user.id,
                'model_id': self.env['ir.model']._get('medical.indication').id,
                'record_id': record.id,
                'action_type': 'unlink',
                'details': f"Indicación médica eliminada por {self.env.user.name}."
            })
        
        return super(MedicalIndication, self).unlink()