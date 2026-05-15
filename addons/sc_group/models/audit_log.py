from odoo import models, fields, api, _
from odoo.exceptions import AccessDenied, AccessError
import logging

_logger = logging.getLogger(__name__)

class AuditLog(models.Model):
    _name = 'audit.log'
    _description = 'Registro de Auditoría'
    _order = 'create_date desc'

    name = fields.Char(string='Descripción', required=True)
    user_id = fields.Many2one('res.users', string='ID Usuario', index=True)
    user_name = fields.Char(string='Usuario', compute="_compute_user_name",index=True, store=True)
    model_id = fields.Many2one('ir.model', string='Modelo')
    model_name = fields.Char(string='Modelo', related='model_id.model', store=True)
    record_id = fields.Integer(string='ID Registro')
    action_type = fields.Selection([
        ('create', 'Crear'),
        ('write', 'Modificar'),
        ('unlink', 'Eliminar'),
        ('login', 'Inicio Sesión'),
        ('logout', 'Cierre Sesión'),
        ('access_denied', 'Acceso Denegado'),
        ('activate_deactivate', 'Activar/Desactivar'),
        ('change_vital_signs','Modificación de signos vitales'), 
    ], 'Tipo de Acción', required=True)
    details = fields.Text('Detalles Adicionales')


    
    @api.depends('user_id')
    def _compute_user_name(self):
        for record in self:
            if record.user_id:
                record.user_name = f"{record.user_id.name} ({record.user_id.login})"
            else:
                record.user_name = "Desconocido"
        
    @api.model        
    def crud_audit_log(self, record, name_model, action_type, extra_details=None):
        """
        Crea un registro en audit.log para la acción especificada.
        :param record: registro individual de uom.category
        :param action_type: 'create', 'write' o 'unlink'
        :param extra_details: texto adicional para el campo details (usado en write)
        """
        # Obtener el ID del modelo 'uom.category' en ir.model
        model = self.env['ir.model'].search([('model', '=', name_model)], limit=1)
        model_id = model.id if model else False

        # Construir el nombre y detalles según el tipo de acción
        if action_type == 'create':
            name = f"Creación {model.name}: {record.display_name}"
            details = f"Se creó {model.name}: {record.display_name}"
        elif action_type == 'write':
            name = f"Modificación {model.name}: {record.display_name}"
            details = extra_details or f"Se modificó {model.name}: {record.display_name}"
        elif action_type == 'unlink':
            name = f"Eliminación {model.name}: {record.display_name}"
            details = f"Se eliminó {model.name}: {record.display_name}"
        else:
            name = f"Acción {action_type} sobre {model.name}"
            details = f"Acción {action_type} sobre {model.name} ID {record.id}"

        # Crear el registro de auditoría
        self.env['audit.log'].sudo().create({
            'name': name,
            'user_id': self.env.user.id,
            'model_id': model_id,
            'record_id': record.id,
            'action_type': action_type,
            'details': details,
        })
    