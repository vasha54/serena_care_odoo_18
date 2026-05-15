from odoo import models, fields, api

class NotImplementedWizard(models.TransientModel):
    _name = 'not.implemented.wizard'
    _description = 'Wizard para funcionalidad no implementada'
    
    message = fields.Char(
        string='Mensaje',
        default="Esta funcionalidad no está implementada en esta versión del sistema",
        readonly=True
    )
    
    @api.model
    def action_show_warning(self, message=None):
        """Método mejorado para mostrar el wizard"""
        wizard_vals = {}
        if message:
            wizard_vals['message'] = message
            
        wizard = self.create(wizard_vals)
        return {
            'name': 'Funcionalidad no disponible',
            'type': 'ir.actions.act_window',
            'res_model': 'not.implemented.wizard',
            'res_id': wizard.id,
            'view_mode': 'form',
            'target': 'new',
            'context': self._context,
        }