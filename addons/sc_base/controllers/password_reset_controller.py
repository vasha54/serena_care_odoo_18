from odoo import http
from odoo.http import request
import json

class PasswordResetController(http.Controller):
    
    @http.route('/web/reset_password', type='http', auth='public', website=True)
    def reset_password(self, **post):
        """Endpoint personalizado para reset de contraseña"""
        if post.get('email'):
            email = post.get('email')
            user = request.env['res.users'].sudo().search([('login', '=', email)], limit=1)
            
            if user:
                try:
                    # Usar el método original de Odoo que hemos extendido
                    user.action_reset_password()
                    return request.render('auth_signup.reset_password_success', {
                        'message': _("Se ha enviado un enlace de recuperación a su email.")
                    })
                except Exception as e:
                    return request.render('auth_signup.reset_password', {
                        'error': str(e)
                    })
            else:
                return request.render('auth_signup.reset_password', {
                    'error': _("No se encontró ningún usuario con ese email.")
                })
        
        return request.render('auth_signup.reset_password')
    
    @http.route('/web/reset_password/confirm', type='http', auth='public', website=True)
    def reset_password_confirm(self, token, **post):
        """Endpoint para confirmar el reset de contraseña"""
        user = request.env['res.users'].sudo().search([
            ('password_reset_token', '=', token)
        ], limit=1)
        
        if not user:
            return request.render('auth_signup.reset_password', {
                'error': _("Token inválido o expirado.")
            })
        
        if post.get('new_password'):
            new_password = post.get('new_password')
            confirm_password = post.get('confirm_password')
            
            try:
                user.change_password(token, new_password, confirm_password)
                return request.render('auth_signup.reset_password_success', {
                    'message': _("Su contraseña ha sido cambiada exitosamente.")
                })
            except Exception as e:
                return request.render('auth_signup.reset_password_confirm', {
                    'token': token,
                    'error': str(e)
                })
        
        return request.render('auth_signup.reset_password_confirm', {
            'token': token
        })