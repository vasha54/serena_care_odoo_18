from odoo import http
from odoo.http import request

class SessionInfoController(http.Controller):
    @http.route('/web/session/get_session_info', type='json', auth='user')
    def get_session_info(self):
        # Obtener la info base de sesión
        info = request.env['ir.http'].session_info()
        # Leer el usuario como sudo para asegurar consistencia
        user = request.env.user.sudo()
        # Añadir ids y listas con nombre si las necesitas en el cliente
        info['selected_residences_ids'] = user.selected_residences_ids.ids
        info['accessible_residences_ids'] = user.accessible_residences_ids.ids
        info['selected_residences'] = [
            {'id': r.id, 'name': r.name} for r in user.selected_residences_ids
        ]
        info['accessible_residences'] = [
            {'id': r.id, 'name': r.name} for r in user.accessible_residences_ids
        ]
        return info
