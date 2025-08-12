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
    ], 'Tipo de Acción', required=True)
    details = fields.Text('Detalles Adicionales')


    
    @api.depends('user_id')
    def _compute_user_name(self):
        for record in self:
            if record.user_id:
                record.user_name = f"{record.user_id.name} ({record.user_id.login})"
            else:
                record.user_name = "Desconocido"
    