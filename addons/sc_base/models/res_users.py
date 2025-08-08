from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied


class ResUser(models.Model):
    _inherit = 'res.users'  # Solo hereda de res.users
    
    # Incluir manualmente los campos/métodos del mixin
    is_deleted = fields.Boolean(
        string="Eliminado",
        default=False,
        index=True,
    )
    
    confirmed_password = fields.Char(
        string="Confirmar contraseña", 
        transient=True,
    )
    
    # Métodos del mixin (copiados directamente)
    def action_soft_delete(self):
        self.write({'is_deleted':True})
        return {
            'type':'ir.actions.client',
             'tag':'reload',
        }

    def action_restore(self):
        self.write({'is_deleted':False})
        return {
            'type':'ir.actions.client',
             'tag':'reload',
        }

    @api.model
    def _auth_credentials_oauth(self, provider, params):
        """Override para verificar is_deleted en autenticación OAuth"""
        uid = super(ResUser, self)._auth_credentials_oauth(provider, params)
        user = self.browse(uid)
        if user.is_deleted:
            raise AccessDenied(_("Usuario eliminado"))
        return uid

    @api.model
    def _auth_credentials(self, login, password):
        """Override para verificar is_deleted en autenticación normal"""
        try:
            uid = super(ResUser, self)._auth_credentials(login, password)
        except AccessDenied as e:
            # Verificar si el error fue por usuario eliminado
            user = self.search([('login', '=', login)], limit=1)
            if user and user.is_deleted:
                raise AccessDenied(_("Usuario eliminado")) from e
            raise

        user = self.browse(uid)
        if user.is_deleted:
            raise AccessDenied(_("Usuario eliminado"))
        return uid

    def _check_credentials(self, password, env):
        """Override para verificar is_deleted en otras autenticaciones"""
        super(ResUser, self)._check_credentials(password, env)
        if self.is_deleted:
            raise AccessDenied(_("Usuario eliminado"))

    