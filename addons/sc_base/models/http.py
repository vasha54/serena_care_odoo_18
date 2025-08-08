
from odoo import http
from odoo.http import Root

class CustomRoot(Root):

    def setup_session(self, httprequest):
        super(CustomRoot, self).setup_session(httprequest)
        # Establecer la cookie como session-only
        httprequest.session.context['session_force_session'] = True

http.Root = CustomRoot