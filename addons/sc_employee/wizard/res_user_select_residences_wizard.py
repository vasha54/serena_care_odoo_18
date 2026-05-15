from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class ResUserSelectResidencesWizard(models.TransientModel):
    _name = 'res.user.select.residences.wizard'
    _description = 'Wizard para seleccionar residencias del usuario'
    
    # Campo para el usuario (generalmente del contexto)
    user_id = fields.Many2one(
        'res.users',
        string='Usuario',
        required=True
    )
    
    # Campo computed para mostrar todas las residencias accesibles (readonly)
    # all_accessible_residences_ids = fields.Many2many(
    #     'residence_house',
    #     string='Todas las residencias accesibles',
    #     related='user_id.accessible_residences_ids',
    #     readonly=True,
    # )
    all_accessible_residences_ids = fields.Many2many(
        'residence_house',
        'res_user_select_wizard_all_rel',  # tabla relacional única
        'wizard_id',                       # columna que apunta al wizard
        'residence_id',                    # columna que apunta a residence_house
        string='Todas las residencias accesibles',
    )

    selected_residences_ids = fields.Many2many(
        'residence_house',
        'res_user_select_wizard_selected_rel',  # otra tabla relacional única
        'wizard_id',                             # columna que apunta al wizard
        'residence_id',                          # columna que apunta a residence_house
        string='Residencias seleccionadas',
    )

    
    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        ctx = self.env.context
        user_id = res.get('user_id') or ctx.get('default_user_id')
        if user_id:
            user = self.env['res.users'].sudo().browse(user_id)
            res['selected_residences_ids'] = [(6, 0, user.selected_residences_ids.ids)]
            res['all_accessible_residences_ids'] = [(6, 0, user.accessible_residences_ids.ids)]
        return res

    def action_update_selected_residences(self):
        self.ensure_one()
        if not self.user_id:
            raise UserError(_('No se ha especificado un usuario.'))
        invalid_residences = self.selected_residences_ids - self.all_accessible_residences_ids
        if invalid_residences:
            raise ValidationError(_('Las siguientes residencias seleccionadas no están entre las accesibles: %s') %
                                ', '.join(invalid_residences.mapped('name')))
        # Escribir con sudo() para evitar bloqueo por reglas
        self.user_id.sudo().write({
            'selected_residences_ids': [(6, 0, self.selected_residences_ids.ids)]
        })
        return {'type': 'ir.actions.client', 'tag': 'reload'}
    
    @api.model
    def _default_user_id(self):
        """Obtiene el usuario desde el contexto"""
        if self.env.context.get('default_user_id'):
            return self.env.context.get('default_user_id')
        return self.env.user.id

    
    
    def action_select_all(self):
        """Selecciona todas las residencias accesibles"""
        self.ensure_one()
        self.selected_residences_ids = self.all_accessible_residences_ids
        return {
            'type': 'ir.actions.act_window',
            'name': 'Filtrar Residencias',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
    
    def action_clear_all(self):
        """Deselecciona todas las residencias"""
        self.ensure_one()
        self.selected_residences_ids = False
        return {
            'type': 'ir.actions.act_window',
            'name': 'Filtrar Residencias',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }