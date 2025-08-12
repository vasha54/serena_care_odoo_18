import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class LogoutController(http.Controller):

    @http.route('/web/session/logout', type='http', auth="user", website=True)
    def custom_logout(self, redirect='/web'):
        """Maneja el cierre de sesión personalizado con registro de auditoría"""
        try:
            # Obtener información del usuario actual
            current_user = request.env.user
            model = request.env['ir.model'].sudo().search([('model', '=', 'res.users')], limit=1)
            
            # Registrar cierre de sesión
            request.env['audit.log'].sudo().create({
                'name': f"Cierre de sesión: {current_user.login}",
                'action_type': 'logout',
                'user_id': current_user.id,
                'model_id': model.id,
                'record_id': current_user.id,
            })
            _logger.info(f"Cierre de sesión registrado: ID {current_user.id}, Login: {current_user.login}")
        except Exception as e:
            _logger.error(f"Error al registrar cierre de sesión: {str(e)}")
        
        # Ejecutar el cierre de sesión estándar
        request.session.logout(keep_db=True)
        return request.redirect(redirect, 303)