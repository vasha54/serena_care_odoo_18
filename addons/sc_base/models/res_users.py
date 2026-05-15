import logging
import re
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied
from odoo import SUPERUSER_ID
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class ResUser(models.Model):
    _inherit = "res.users"

    is_user_sc = fields.Boolean(
        string="Es usuario de Serena Care",
        default=False,
    )
    is_deleted = fields.Boolean(
        string="Eliminado",
        default=False,
        index=True,
    )
    confirmed_password = fields.Char(
        string="Confirmar contraseña",
        transient=True,
    )
    password_reset_token = fields.Char(string="Token de Reset")
    password_reset_token_expiry = fields.Datetime(string="Expiración del Token")
    password_reset_attempts = fields.Integer(string="Intentos de Reset", default=0)
    last_password_reset_attempt = fields.Datetime(string="Último Intento de Reset")

    serena_group_ids = fields.Many2many(
        'res.groups',
        string='Grupos Serena',
        compute='_compute_serena_groups',
        inverse='_inverse_serena_groups',
        store=False,
        domain="[('category_id.name', '=', 'Serena')]"
    )
    # Campos computados para verificar pertenencia a grupos
    has_gs_admin = fields.Boolean(compute='_compute_has_groups')
    has_gs_admin_direccion = fields.Boolean(compute='_compute_has_groups')
    has_gs_admin_gerente_ti = fields.Boolean(compute='_compute_has_groups')
    has_gs_admin_gerente_enfermeria = fields.Boolean(compute='_compute_has_groups')
    has_gs_admin_coordinadora_enfermeria = fields.Boolean(compute='_compute_has_groups')
    has_gs_gerente_salud = fields.Boolean(compute='_compute_has_groups')
    has_gs_gerente_salud_medico = fields.Boolean(compute='_compute_has_groups')
    has_gs_enfermeria = fields.Boolean(compute='_compute_has_groups')
    has_gs_enfermeria_cuidador = fields.Boolean(compute='_compute_has_groups')

    def get_current_user_id(self):
        """Devuelve el ID del usuario actual"""
        return self.env.user.id
    
    @api.depends('serena_group_ids')
    def _compute_has_groups(self):
        """Calcula si el usuario tiene cada grupo específico"""
        # Obtener referencias a todos los grupos una sola vez
        group_refs = {
            'has_gs_admin': 'sc_group.gs_admin',
            'has_gs_admin_direccion': 'sc_group.gs_admin_direccion',
            'has_gs_admin_gerente_ti': 'sc_group.gs_admin_gerente_ti',
            'has_gs_admin_gerente_enfermeria': 'sc_group.gs_admin_gerente_enfermeria',
            'has_gs_admin_coordinadora_enfermeria': 'sc_group.gs_admin_coordinadora_enfermeria',
            'has_gs_gerente_salud': 'sc_group.gs_gerente_salud',
            'has_gs_gerente_salud_medico': 'sc_group.gs_gerente_salud_medico',
            'has_gs_enfermeria': 'sc_group.gs_enfermeria',
            'has_gs_enfermeria_cuidador': 'sc_group.gs_enfermeria_cuidador',
        }
        
        # Inicializar todos los campos en False
        for field in group_refs.keys():
            for user in self:
                user[field] = False
        
        # Para cada usuario, verificar cada grupo
        for user in self:
            for field_name, xmlid in group_refs.items():
                try:
                    group = self.env.ref(xmlid)
                    user[field_name] = group in user.serena_group_ids
                except ValueError:
                    # Si el grupo no existe (por ejemplo, módulo no instalado)
                    user[field_name] = False
    
    @api.depends('groups_id')
    def _compute_serena_groups(self):
        for user in self:
            # Obtener solo grupos de la categoría Serena
            serena_category = self.env['ir.module.category'].search([('name', '=', 'Serena')], limit=1)
            if serena_category:
                serena_groups = user.groups_id.filtered(lambda g: g.category_id == serena_category)
                user.serena_group_ids = serena_groups
            else:
                user.serena_group_ids = False
    
    def _inverse_serena_groups(self):
        for user in self:
            serena_category = self.env['ir.module.category'].search([('name', '=', 'Serena')], limit=1)
            if serena_category:
                # Remover grupos Serena actuales
                current_serena = user.groups_id.filtered(lambda g: g.category_id == serena_category)
                user.groups_id = [(3, g.id) for g in current_serena]
                
                # Agregar nuevos grupos Serena
                if user.serena_group_ids:
                    user.groups_id = [(4, g.id) for g in user.serena_group_ids]

    def _validate_password_security(self, password):
        """Valida los requisitos de seguridad de la contraseña"""
        if len(password) < 8:
            raise ValidationError(_("La contraseña debe tener al menos 8 caracteres."))

        if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
            raise ValidationError(_("La contraseña debe contener letras y números."))

        # Puedes agregar más validaciones aquí
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(
                _("La contraseña debe contener al menos un carácter especial.")
            )

        return True

    def _create_password_reset_audit_log(self, action_type, details, success=True):
        """Crea registro de auditoría para recuperación de contraseña"""
        try:
            self.env["audit.log"].create(
                {
                    "name": f"Recuperación de Contraseña - {'Éxito' if success else 'Fallido'}",
                    "user_id": self.id,
                    "model_id": self.env["ir.model"]
                    .search([("model", "=", "res.users")], limit=1)
                    .id,
                    "record_id": self.id,
                    "action_type": "write" if success else "access_denied",
                    "details": details,
                }
            )
        except Exception as e:
            _logger.error(f"Error creando registro de auditoría: {str(e)}")

    def _is_password_reset_token_valid(self, token):
        """Verifica si el token de reset es válido y no ha expirado"""
        if not self.password_reset_token or self.password_reset_token != token:
            return False

        if not self.password_reset_token_expiry:
            return False

        now = datetime.now()
        expiry_date = fields.Datetime.from_string(self.password_reset_token_expiry)
        return now <= expiry_date

    def _check_password_reset_attempts(self):
        """Verifica y controla los intentos de reset de contraseña"""
        max_attempts = 5
        lockout_duration = 30  # minutos

        now = datetime.now()

        if self.last_password_reset_attempt:
            last_attempt = fields.Datetime.from_string(self.last_password_reset_attempt)
            time_diff = (now - last_attempt).total_seconds() / 60

            # Si han pasado más de lockout_duration minutos, resetear contador
            if time_diff > lockout_duration:
                self.password_reset_attempts = 0
            elif self.password_reset_attempts >= max_attempts:
                raise ValidationError(
                    _("Demasiados intentos fallidos. Por favor espere %d minutos.")
                    % lockout_duration
                )

    def action_reset_password(self):
        """Sobrescribe el método de reset de contraseña para agregar auditoría"""
        # Registrar intento de solicitud de reset
        self._create_password_reset_audit_log(
            "write",
            f"Solicitud de recuperación de contraseña enviada para el usuario: {self.login}",
        )

        # Llamar al método original
        return super().action_reset_password()

    def _set_password_reset_token(self):
        """Genera y establece un token de reset con expiración"""
        token = self._generate_password_reset_token()
        expiry_time = datetime.now() + timedelta(hours=24)  # Token expira en 24 horas

        self.write(
            {"password_reset_token": token, "password_reset_token_expiry": expiry_time}
        )

        return token

    def _generate_password_reset_token(self):
        """Genera un token único para reset de contraseña"""
        import secrets
        import string

        alphabet = string.ascii_letters + string.digits
        token = "".join(secrets.choice(alphabet) for _ in range(32))
        return token

    def change_password(self, token, new_password, confirm_password):
        """Sobrescribe el método de cambio de contraseña para agregar validaciones"""
        # Verificar intentos
        self._check_password_reset_attempts()

        # Verificar token
        if not self._is_password_reset_token_valid(token):
            self.password_reset_attempts += 1
            self.last_password_reset_attempt = datetime.now()

            self._create_password_reset_audit_log(
                "access_denied",
                f"Intento fallido de cambio de contraseña - Token inválido o expirado para usuario: {self.login}",
                success=False,
            )

            raise ValidationError(_("Token inválido o expirado."))

        # Verificar que las contraseñas coincidan
        if new_password != confirm_password:
            self.password_reset_attempts += 1
            self.last_password_reset_attempt = datetime.now()

            self._create_password_reset_audit_log(
                "access_denied",
                f"Las contraseñas no coinciden para usuario: {self.login}",
                success=False,
            )

            raise ValidationError(_("Las contraseñas no coinciden."))

        # Validar seguridad de la contraseña
        self._validate_password_security(new_password)

        try:
            # Cambiar la contraseña
            result = super(ResUser, self).change_password(new_password)

            # Limpiar token y contadores después de éxito
            self.write(
                {
                    "password_reset_token": False,
                    "password_reset_token_expiry": False,
                    "password_reset_attempts": 0,
                    "last_password_reset_attempt": False,
                }
            )

            # Registrar éxito en auditoría
            self._create_password_reset_audit_log(
                "write",
                f"Contraseña cambiada exitosamente para usuario: {self.login}",
                success=True,
            )

            return result

        except Exception as e:
            # Registrar error en auditoría
            self._create_password_reset_audit_log(
                "access_denied",
                f"Error al cambiar contraseña: {str(e)} para usuario: {self.login}",
                success=False,
            )
            raise

    def action_soft_delete(self):
        self.write({"is_deleted": True})
        model = (
            self.env["ir.model"].sudo().search([("model", "=", "res.users")], limit=1)
        )
        for record in self:
            self.env["audit.log"].sudo().create(
                {
                    "name": f"Usuario eliminado: {record.login}",
                    "action_type": "unlink",
                    "user_id": self.env.user.id,
                    "model_id": model.id,  # Asignar ID del modelo
                    "record_id": record.id,  # ID del registro afectado
                }
            )
            _logger.info(
                f"Usuario eliminado (soft delete): ID {record.id}, Login: {record.login}"
            )
        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }

    def action_restore(self):
        self.write({"is_deleted": False})
        _logger.info(f"Usuario restaurado: ID {self.id}, Login: {self.login}")
        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }

    @classmethod
    def _login(cls, db, credential, user_agent_env):
        try:
            uid = super()._login(db, credential, user_agent_env)
            if not uid:
                raise AccessDenied(_("Invalid credentials"))

            user_id = uid.get("uid", 0)
            with cls.pool.cursor() as cr:
                env = api.Environment(cr, SUPERUSER_ID, {})
                user = env["res.users"].sudo().browse(user_id)
                AuditLog = env["audit.log"].sudo()
                IrModel = env["ir.model"].sudo()
                model = IrModel.search([("model", "=", "res.users")], limit=1)

                # OBTENER LA DIRECCIÓN IP
                ip_address = "IP no disponible"
                # Método 1: Desde user_agent_env si está disponible
                if user_agent_env and hasattr(user_agent_env, "get"):
                    ip_address = user_agent_env.get("remote_addr", "IP no disponible")

                # Método alternativo: Desde el objeto request si está disponible
                if ip_address == "IP no disponible":
                    try:
                        from odoo import http

                        request = http.request
                        if request:
                            # Intentar obtener IP desde headers comunes
                            if request.httprequest.headers.get("X-Forwarded-For"):
                                ip_address = request.httprequest.headers.get(
                                    "X-Forwarded-For"
                                ).split(",")[0]
                            elif request.httprequest.headers.get("X-Real-IP"):
                                ip_address = request.httprequest.headers.get(
                                    "X-Real-IP"
                                )
                            else:
                                ip_address = request.httprequest.remote_addr
                    except Exception:
                        pass

                # Verificar si el usuario existe y está eliminado
                if not user.exists():
                    AuditLog.create(
                        {
                            "name": "Acceso denegado: usuario no existe",
                            "action_type": "access_denied",
                            "user_id": False,
                            "model_id": model.id,
                            "record_id": False,
                            "details": f"Intento de acceso: {credential['login']} - IP: {ip_address}",
                        }
                    )
                    raise AccessDenied()

                if user.is_deleted:
                    AuditLog.create(
                        {
                            "name": "Acceso denegado: usuario eliminado",
                            "action_type": "access_denied",
                            "user_id": user.id,
                            "model_id": model.id,
                            "record_id": user.id,
                            "details": f"IP: {ip_address}",
                        }
                    )
                    raise AccessDenied()

                # Registrar login exitoso con IP
                AuditLog.create(
                    {
                        "name": f"Inicio de sesión de {user.name} ({user.login})",
                        "action_type": "login",
                        "user_id": user.id,
                        "model_id": model.id,
                        "record_id": user.id,
                        "details": f"IP: {ip_address} - User Agent: {user_agent_env}",
                    }
                )
            return uid
        except AccessDenied as e:
            # Registrar intentos fallidos con IP
            with cls.pool.cursor() as cr:
                env = api.Environment(cr, SUPERUSER_ID, {})
                user = (
                    env["res.users"]
                    .sudo()
                    .search([("login", "=", credential["login"])], limit=1)
                )
                AuditLog = env["audit.log"].sudo()
                IrModel = env["ir.model"].sudo()
                model = IrModel.search([("model", "=", "res.users")], limit=1)

                # OBTENER LA DIRECCIÓN IP (mismo código que arriba)
                ip_address = "IP no disponible"
                if user_agent_env and hasattr(user_agent_env, "get"):
                    ip_address = user_agent_env.get("remote_addr", "IP no disponible")

                if ip_address == "IP no disponible":
                    try:
                        from odoo import http

                        request = http.request
                        if request:
                            if request.httprequest.headers.get("X-Forwarded-For"):
                                ip_address = request.httprequest.headers.get(
                                    "X-Forwarded-For"
                                ).split(",")[0]
                            elif request.httprequest.headers.get("X-Real-IP"):
                                ip_address = request.httprequest.headers.get(
                                    "X-Real-IP"
                                )
                            else:
                                ip_address = request.httprequest.remote_addr
                    except Exception:
                        pass

                details = "Credenciales inválidas"
                if user:
                    if user.is_deleted:
                        details = "Usuario eliminado"
                    elif not user.active:
                        details = "Usuario inactivo"

                AuditLog.create(
                    {
                        "name": f"Acceso denegado: {credential['login']}",
                        "action_type": "access_denied",
                        "user_id": user.id if user else False,
                        "model_id": model.id,
                        "record_id": user.id if user else False,
                        "details": f"{details} - IP: {ip_address}",
                    }
                )
            raise
        except Exception as e:
            _logger.exception("Error durante el login")
            raise

    def action_logout(self):
        """Registra el cierre de sesión en audit.log"""
        # Obtener información del usuario actual
        current_user = self.env.user
        model = (
            self.env["ir.model"].sudo().search([("model", "=", "res.users")], limit=1)
        )

        # Registrar antes de cerrar la sesión
        self.env["audit.log"].sudo().create(
            {
                "name": f"Cierre de sesión: {current_user.login}",
                "action_type": "logout",
                "user_id": current_user.id,
                "model_id": model.id,
                "record_id": current_user.id,
            }
        )
        _logger.info(
            f"Cierre de sesión registrado: ID {current_user.id}, Login: {current_user.login}"
        )

        # Llamar al método original para cerrar sesión
        return super().action_logout()

    def _check_session_validity(self, db, uid, sid):
        """Registra cierre de sesión por inactividad"""
        result = super()._check_session_validity(db, uid, sid)

        if not result:  # Sesión expirada
            with self.pool.cursor() as cr:
                env = api.Environment(cr, SUPERUSER_ID, {})
                user = env["res.users"].sudo().browse(uid)
                if user:
                    model = (
                        env["ir.model"]
                        .sudo()
                        .search([("model", "=", "res.users")], limit=1)
                    )
                    env["audit.log"].sudo().create(
                        {
                            "name": f"Cierre de sesión por inactividad: {user.login}",
                            "action_type": "logout",
                            "user_id": user.id,
                            "model_id": model.id,
                            "record_id": user.id,
                        }
                    )
                    _logger.info(f"Sesión expirada: ID {user.id}, Login: {user.login}")

        return result

    def logout(self):
        """Registra el cierre de sesión en audit.log"""
        # Obtener información del usuario actual
        current_user = self.env.user
        model = (
            self.env["ir.model"].sudo().search([("model", "=", "res.users")], limit=1)
        )

        # Registrar antes de cerrar la sesión
        self.env["audit.log"].sudo().create(
            {
                "name": f"Cierre de sesión: {current_user.login}",
                "action_type": "logout",
                "user_id": current_user.id,
                "model_id": model.id,
                "record_id": current_user.id,
            }
        )
        _logger.info(
            f"Cierre de sesión registrado: ID {current_user.id}, Login: {current_user.login}"
        )

        # Llamar al método original para cerrar sesiónw
        return super().logout()

    @api.constrains("groups_id")
    def _check_no_inactive_groups_assigned(self):
        for user in self:
            # cualquier grupo inactivo en groups_id -> error
            inactive = user.groups_id.filtered(lambda g: not g.active)
            if inactive:
                names = ", ".join(inactive.mapped("name"))
                raise ValidationError(
                    _("No se puede asignar el/los grupo(s) inactivo(s): %s") % names
                )
           
    @api.model
    def create(self, values):
        records = super().create(values)
        # Crear log de auditoría para cada registro creado
        for record in records:
            self.env['audit.log'].sudo().crud_audit_log(record, 'res.users', 'create')
        return records

    def write(self, values):
        # Guardar estado anterior para detectar cambios (opcional, mejora la calidad del detalle)
        old_values = {}
        for record in self:
            old_values[record.id] = {
                field: record[field] for field in values if field in record._fields and not record._fields[field].compute
            }
        result = super().write(values)
        # Después de la escritura, crear logs con los campos modificados
        for record in self:
            changed_fields = []
            for field, new_val in values.items():
                if field in old_values.get(record.id, {}):
                    old_val = old_values[record.id][field]
                    if old_val != record[field]:
                        changed_fields.append(f"{field}: {old_val!r} -> {record[field]!r}")
                else:
                    # Campo no almacenado o no presente en el registro anterior, se registra igual
                    changed_fields.append(f"{field}: {record[field]!r}")
            if changed_fields:
                details = "Campos modificados: " + "; ".join(changed_fields)
            else:
                details = "Modificación sin cambios detectados"
            self.env['audit.log'].sudo().crud_audit_log(record, 'res.users', 'write', extra_details=details)
        return result

    def unlink(self):
        # Antes de eliminar, crear logs para cada registro
        for record in self:
            self.env['audit.log'].sudo().crud_audit_log(record, 'res.users', 'unlink')
        return super().unlink()

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
