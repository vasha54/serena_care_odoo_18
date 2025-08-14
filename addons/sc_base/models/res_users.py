import logging
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied
from odoo import SUPERUSER_ID

_logger = logging.getLogger(__name__)

class ResUser(models.Model):
    _inherit = 'res.users'
    
    is_deleted = fields.Boolean(
        string="Eliminado",
        default=False,
        index=True,
    )
    
    confirmed_password = fields.Char(
        string="Confirmar contraseña", 
        transient=True,
    )
    
    def action_soft_delete(self):
        self.write({'is_deleted': True})
        model = self.env['ir.model'].sudo().search([('model', '=', 'res.users')], limit=1)
        self.env['audit.log'].sudo().create({
            'name': f"Usuario eliminado: {self.login}",
            'action_type': 'unlink',
            'user_id': self.env.user.id,
            'model_id': model.id,  # Asignar ID del modelo
            'record_id': self.id,  # ID del registro afectado
        })
        _logger.info(f"Usuario eliminado (soft delete): ID {self.id}, Login: {self.login}")
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def action_restore(self):
        self.write({'is_deleted': False})
        _logger.info(f"Usuario restaurado: ID {self.id}, Login: {self.login}")
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
    
    @classmethod 
    def _login(cls, db, credential, user_agent_env):
        try:
            uid = super()._login(db, credential, user_agent_env)
            if not uid:
                raise AccessDenied(_("Invalid credentials"))
            
            user_id = uid.get('uid',0)
            with cls.pool.cursor() as cr:
                env = api.Environment(cr,SUPERUSER_ID,{})            
                user = env['res.users'].sudo().browse(user_id)
                AuditLog = env['audit.log'].sudo()
                IrModel = env['ir.model'].sudo()
                model = IrModel.search([('model', '=', 'res.users')], limit=1)
                # Verificar si el usuario existe y está eliminado
                if not user.exists():
                    AuditLog.create({
                        'name': "Acceso denegado: usuario no existe",
                        'action_type': 'access_denied',
                        'user_id': False,
                        'model_id': model.id,
                        'record_id': False,
                        'details': f"Intento de acceso: {credential['login']}",
                    })
                    raise AccessDenied()
                
                if user.is_deleted:
                    AuditLog.create({
                        'name': "Acceso denegado: usuario eliminado",
                        'action_type': 'access_denied',
                        'user_id': user.id,
                        'model_id': model.id,
                        'record_id': user.id,
                    })
                    raise AccessDenied()
                AuditLog.create({
                    'name':  f"Inicio de sesión de {user.name} ({user.login})",
                    'action_type': 'login',
                    'user_id': user.id,
                    'model_id': model.id,  # Asignar ID del modelo
                    'record_id': user.id,
                    })
            return uid  
        except AccessDenied as e:
            # Registrar intentos fallidos
            with cls.pool.cursor() as cr:
                env = api.Environment(cr, SUPERUSER_ID, {})
                user = env['res.users'].sudo().search([('login', '=',credential['login'])], limit=1)
                AuditLog = env['audit.log'].sudo()
                IrModel = env['ir.model'].sudo()
                model = IrModel.search([('model', '=', 'res.users')], limit=1)
                
                details = "Credenciales inválidas"
                if user:
                    if user.is_deleted:
                        details = "Usuario eliminado"
                    elif not user.active:
                        details = "Usuario inactivo"
                
                AuditLog.create({
                    'name': f"Acceso denegado: {credential['login']}",
                    'action_type': 'access_denied',
                    'user_id': user.id if user else False,
                    'model_id': model.id,
                    'record_id': user.id if user else False,
                    'details': details,
                })
            raise
        except Exception as e:
            _logger.exception("Error durante el login")
            raise 
    
    def action_logout(self):
        """Registra el cierre de sesión en audit.log"""
        # Obtener información del usuario actual
        current_user = self.env.user
        model = self.env['ir.model'].sudo().search([('model', '=', 'res.users')], limit=1)
        
        # Registrar antes de cerrar la sesión
        self.env['audit.log'].sudo().create({
            'name': f"Cierre de sesión: {current_user.login}",
            'action_type': 'logout',
            'user_id': current_user.id,
            'model_id': model.id,
            'record_id': current_user.id,
        })
        _logger.info(f"Cierre de sesión registrado: ID {current_user.id}, Login: {current_user.login}")
        
        # Llamar al método original para cerrar sesión
        return super().action_logout()

    def _check_session_validity(self, db, uid, sid):
        """Registra cierre de sesión por inactividad"""
        result = super()._check_session_validity(db, uid, sid)
    
        if not result:  # Sesión expirada
            with self.pool.cursor() as cr:
                env = api.Environment(cr, SUPERUSER_ID, {})
                user = env['res.users'].sudo().browse(uid)
                if user:
                    model = env['ir.model'].sudo().search([('model', '=', 'res.users')], limit=1)
                    env['audit.log'].sudo().create({
                        'name': f"Cierre de sesión por inactividad: {user.login}",
                        'action_type': 'logout',
                        'user_id': user.id,
                        'model_id': model.id,
                        'record_id': user.id,
                    })
                    _logger.info(f"Sesión expirada: ID {user.id}, Login: {user.login}")
    
        return result

    def logout(self):
        """Registra el cierre de sesión en audit.log"""
        # Obtener información del usuario actual
        current_user = self.env.user
        model = self.env['ir.model'].sudo().search([('model', '=', 'res.users')], limit=1)
        
        # Registrar antes de cerrar la sesión
        self.env['audit.log'].sudo().create({
            'name': f"Cierre de sesión: {current_user.login}",
            'action_type': 'logout',
            'user_id': current_user.id,
            'model_id': model.id,
            'record_id': current_user.id,
        })
        _logger.info(f"Cierre de sesión registrado: ID {current_user.id}, Login: {current_user.login}")
        
        # Llamar al método original para cerrar sesiónw 
        return super().logout()
      
        

    

    

# import logging
# from odoo import models, fields, api, _
# from odoo.exceptions import ValidationError, AccessDenied

# _logger = logging.getLogger(__name__)

# class ResUser(models.Model):
#     _inherit = 'res.users'
    
#     is_deleted = fields.Boolean(
#         string="Eliminado",
#         default=False,
#         index=True,
#     )
    
#     confirmed_password = fields.Char(
#         string="Confirmar contraseña", 
#         transient=True,
#     )
    
#     def action_soft_delete(self):
#         self.write({'is_deleted': True})
#         _logger.info(f"Usuario eliminado (soft delete): ID {self.id}, Login: {self.login}")
#         
#         return {
#             'type': 'ir.actions.client',
#             'tag': 'reload',
#         }

#     def action_restore(self):
#         self.write({'is_deleted': False})
#         _logger.info(f"Usuario restaurado: ID {self.id}, Login: {self.login}")
#         return {
#             'type': 'ir.actions.client',
#             'tag': 'reload',
#         }

    

#     @api.model
#     def _auth_credentials_oauth(self, provider, params):
#         """Log para autenticación OAuth"""
#         try:
#             uid = super()._auth_credentials_oauth(provider, params)
#             user = self.browse(uid)
#             if user.is_deleted:
#                 _logger.warning(f"Intento de acceso OAuth fallido (usuario eliminado): Provider {provider}, Login: {user.login}")
#                 raise AccessDenied(_("Usuario eliminado"))
            
#             _logger.info(f"Autenticación OAuth exitosa: ID {user.id}, Login: {user.login}, Provider: {provider}")
#             return uid
#         except AccessDenied as e:
#             _logger.warning(f"Autenticación OAuth fallida: Provider {provider}, Error: {str(e)}")
#             raise

#     @api.model
#     def _auth_credentials(self, login, password):
#         """Log para autenticación estándar"""
#         try:
#             uid = super()._auth_credentials(login, password)
#             user = self.browse(uid)
            
#             if user.is_deleted:
#                 _logger.warning(f"Intento de acceso fallido (usuario eliminado): Login: {login}")
#                 raise AccessDenied(_("Usuario eliminado"))
            
#             _logger.info(f"Autenticación estándar exitosa: ID {user.id}, Login: {user.login}")
#             return uid
#         except AccessDenied as e:
#             # Registrar diferentes tipos de errores
#             user = self.search([('login', '=', login)], limit=1)
#             if user:
#                 if user.is_deleted:
#                     error_type = "usuario eliminado"
#                 else:
#                     error_type = "credenciales inválidas"
#             else:
#                 error_type = "usuario no existe"
#             # Obtener el modelo 'res.users'
#             # model = self.env['ir.model'].sudo().search([('model', '=', 'res.users')], limit=1)
        
#             # self.env['audit.log'].sudo().create({
#             #     'name': f"Acceso denegado: {login}",
#             #     'action_type': 'access_denied',
#             #     'user_id': user.id if user else False,
#             #     'model_id': model.id,  # Asignar ID del modelo
#             #     'record_id': user.id if user else False,
#             #     'details': f"Tipo: {error_type}",
#             # })
#             _logger.warning(f"Autenticación estándar fallida: Login: {login}, Tipo: {error_type}")
#             raise

#     def _check_credentials(self, password):
#         super()._check_credentials(password)
#         if self.is_deleted:
#             raise AccessDenied(_("Usuario eliminado"))

        

#     @api.model
#     def action_logout(self):
#         """Log para cierre de sesión"""
#         current_user = self.env.user
#         _logger.info(f"Cierre de sesión iniciado: ID {current_user.id}, Login: {current_user.login}")
#         result = super().action_logout()
#         
#         _logger.info(f"Cierre de sesión exitoso: ID {current_user.id}, Login: {current_user.login}")
#         return result

#     def _register_session(self, session, env):
#         """Log para inicio de sesión exitoso"""
#         
#         _logger.info(f"Sesión iniciada: ID {self.id}, Login: {self.login}, Session ID: {session.sid}")
#         return res
