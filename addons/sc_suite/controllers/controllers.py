from odoo import http
from odoo.http import request

class DashboardController(http.Controller):
    
    @http.route('/serena_care_dashboard', type='http', auth='user', website=True)
    def render_dashboard(self, **kwargs):
        # Obtener datos para el dashboard
        user = request.env.user
        # Aquí puedes agregar lógica para obtener datos específicos
        
        values = {
            'user': user,
            'company': user.company_id,
        }
        
        return request.render('sc_suite.dashboard_template', values)