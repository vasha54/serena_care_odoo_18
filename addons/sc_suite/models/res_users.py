from odoo import models, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def _get_home_action(self):
        # # Redirigir al dashboard personalizado
        # action = self.env.ref('sc_suite.action_serena_care_dashboard', raise_if_not_found=False)
        # if action:
        #     return action.read()[0]
        return super()._get_home_action()