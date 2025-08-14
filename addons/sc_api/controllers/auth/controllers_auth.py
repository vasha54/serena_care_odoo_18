import json
import datetime
import jwt
import logging
import odoo

from odoo import _, http
from odoo.http import Response, request
from odoo.exceptions import AccessDenied
from odoo.modules.registry import Registry

from ..controllers_base import BaseAPIController

_logger = logging.getLogger(__name__)

class AuthAPIController(BaseAPIController):

    @http.route(
        "/api_serena/v1/login",
        type='json', 
        auth="none", 
        methods=['POST'], 
        csrf=False
    )
    def login(self, **post):
        """
    Autentica al usuario y genera un token JWT
    ---
    tags:
      - Authentication
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - login
              - password
              - residence_id
            properties:
              login:
                type: string
                description: Email o nombre de usuario
              password:
                type: string
                description: Contraseña
              residence_id:
                type: integer
                description: ID de la residencia del usuario
    responses:
      200:
        description: Autenticación exitosa
        content:
          application/json:
            schema:
              type: object
              properties:
                status:
                  type: string
                  example: success
                session_id:
                  type: string
                  example: "request.session.sid"
                user:
                  type: object
                  properties:
                    id:
                      type: integer
                      example: 1
                    name:
                      type: string
                      example: "Admin"
                    login:
                      type: string
                      example: "admin"
                    token:
                      type: string
                      example: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
                    token_expiration:
                      type: string
                      format: date-time
                      example: "2025-08-06T18:30:45"
                residence_id:
                  type: integer
                  example: 1
      400:
        description: Parámetros faltantes o inválidos
      401:
        description: Credenciales inválidas
      500:
        description: Error interno del servidor
    """
        try:
            # Obtener datos del JSON
            data = self._get_json_data(request.httprequest.data)
            self._check_existence_parameters(['login','password','residence_id'], data)
            
            login = data['login']
            password = data['password']
            residence_id = data['residence_id']
            current_db = request.env.cr.dbname
        
            answer = {}
            # Usar Registry directamente como recomienda el warning
            registry = Registry(current_db)
            with registry.cursor() as cr:
                env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
                
                # Crear el diccionario de credenciales requerido
                credentials = {
                    'type': 'password',  # Tipo de autenticación
                    'login': login,      # Nombre de usuario
                    'password': password  # Contraseña
                }

                # Usar el método authenticate del modelo res.users
                uid = env['res.users'].authenticate(current_db, credentials, {})
                if not uid:
                    raise AccessDenied(_("Invalid credentials"))
                
                _logger.info(f"User autenticate with uid:{uid}")
                uid = uid.get('uid',0)
                user = env['res.users'].sudo().browse(uid)
                
                if not user:
                   raise Exception("Usuario no encontrado")

                if user.jwt_token or user.token_expiration:
                   raise Exception(f"Ya el usuario tiene una sesión iniciada que expira: {user.token_expiration}")

                # Crear sesión manualmente
                # request.session.authenticate(db_name, login, password)
                self._check_access_residences(env, user.id, residence_id)
                # Generar token JWT
                expiration = datetime.datetime.now() + datetime.timedelta(hours=8)
                payload = {
                    "user_id": user.id,
                    "exp": expiration,
                    "residence_id": residence_id,         
                }
                token = jwt.encode(payload, BaseAPIController.SECRET_KEY, algorithm=BaseAPIController.ALGORITHM)
                _logger.info(f"Token: {token}")
                user.sudo().write({
                    "jwt_token": token,
                    "token_expiration": expiration
                })
                answer = {
                    "status": "success",
                    "user": {
                        "id": user.id,
                        "name": user.name,
                        "login": user.login,
                        "token": user.jwt_token,
                        "token_expiration": self._convert_to_iso(user.token_expiration),
                    },
                    "residence_id": residence_id
                }
            _logger.info(f"Response: {answer}")
            return Response(
                    json.dumps(answer), headers={"Content-Type": "application/json"}
                )
        except Exception as e:
            return self._handle_error(e)
        

    @http.route(
        "/api_serena/v1/logout",
        type='json', 
        auth="none", 
        methods=['POST'], 
        csrf=False
    )
    def logout(self, **post):
        """
    Cierra la sesión e invalida el token JWT
    ---
    tags:
      - Authentication
    security:
      - bearerAuth: []
    responses:
      200:
        description: Sesión cerrada exitosamente
        content:
          application/json:
            schema:
              type: object
              properties:
                status:
                  type: string
                  example: success
                message:
                  type: string
                  example: "Sesión cerrada correctamente"
                data:
                  type: null
                pagination:
                  type: null
      400:
        description: Token no proporcionado o inválido
      401:
        description: Token expirado o no autorizado
      500:
        description: Error interno del servidor
    """
        try:
            # Extraer token del encabezado Authorization
            auth_header = http.request.httprequest.headers.get('Authorization')
            if not auth_header or 'Bearer ' not in auth_header:
                raise Exception("Encabezado de autorización inválido")
            
            token = auth_header.split('Bearer ')[1].strip()
            current_db = request.env.cr.dbname
        
            answer = {}
            # Usar Registry directamente como recomienda el warning
            registry = Registry(current_db)
            with registry.cursor() as cr:
                env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
                payload = jwt.decode(token, BaseAPIController.SECRET_KEY, algorithms=[BaseAPIController.ALGORITHM])
                user_id = payload['user_id']
                users = env['res.users'].sudo().search([("id","=",user_id),("jwt_token","=",token)])
                if users:
                    # Invalidar token en base de datos
                    users.sudo().write({
                        "jwt_token": False,
                        "token_expiration": False
                        })
                    answer = {
                        "status": "success",
                        "message":"Sesión cerrada correctamente",
                        "data": None,
                        "pagination": None,
                    }
                else:
                    answer = {
                        "status": "error",
                        "message":"Usuario no encontrado en el sistema",
                        "data": None,
                        "pagination": None,
                    }
            _logger.info(f"Response: {answer}")
            return Response(
                json.dumps(answer), headers={"Content-Type": "application/json"}
            )    
        except Exception as e:
            return self._handle_error(e)
            
        

        
        

    