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

    @http.route('/web/binary/company_logo', type='http', auth="none")
    def company_logo(self, db=None, **kwargs):
        # Lógica para servir tu logo personalizado
        return request.redirect('/sc_suite/static/img/serena_care.png')