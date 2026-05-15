import json
import jwt
import logging
import odoo

from datetime import datetime, timedelta

from odoo import _, http
from odoo.http import Response, request 
from odoo.exceptions import AccessDenied
from odoo.modules.registry import Registry

from ..controllers_base import BaseAPIController

_logger = logging.getLogger(__name__)

class AuthAPIController(BaseAPIController):

    def doc_login(self):
        """
        Documentación Swagger para el método login
        """
        return {
            "tags": ["Autenticación"],
            "summary": "Autenticarse en el sistema",
            "description": "Endpoint para autenticar usuarios y obtener token JWT de acceso",
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "required": ["login", "password", "residence_id"],
                            "properties": {
                                "login": {
                                    "type": "string",
                                    "description": "Usuario con el cual se va a autenticar",
                                    "example": "carlos_ruiz"
                                },
                                "password": {
                                    "type": "string",
                                    "description": "Contraseña de acceso",
                                    "example": "C4rl0s.Ru1z*"
                                },
                                "residence_id": {
                                    "type": "integer",
                                    "description": "Identificador de la residencia en la que se desea autenticar",
                                    "example": 4
                                }
                            }
                        },
                        "example": {
                            "login": "carlos_ruiz",
                            "password": "C4rl0s.Ru1z*",
                            "residence_id": 4
                        }
                    }
                }
            },
            "responses": {
                "200": {
                    "description": "Autenticación exitosa",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "status": {
                                        "type": "string",
                                        "description": "Indica si la consulta se ejecutó correctamente (success) o ocurrió un error (error)",
                                        "example": "success"
                                    },
                                    "message": {
                                        "type": "string",
                                        "description": "Mensaje de error si la ejecución tuvo problemas",
                                        "example": "Access Denied"
                                    },
                                    "data": {
                                        "type": "null",
                                        "description": "Presente con valor None si no se pudo realizar la autenticación"
                                    },
                                    "pagination": {
                                        "type": "null",
                                        "description": "Presente con valor None si no se pudo realizar la autenticación"
                                    },
                                    "user": {
                                        "type": "object",
                                        "description": "Presente solo si la autenticación fue exitosa",
                                        "properties": {
                                            "id": {
                                                "type": "integer",
                                                "description": "Identificador numérico del usuario en el sistema",
                                                "example": 82
                                            },
                                            "name": {
                                                "type": "string",
                                                "description": "Nombre de la persona autenticada",
                                                "example": "Dr. Jorge Ramírez Jimenez"
                                            },
                                            "login": {
                                                "type": "string",
                                                "description": "Usuario de la persona autenticada",
                                                "example": "jorge_ramirez"
                                            },
                                            "token": {
                                                "type": "string",
                                                "description": "Token del usuario para realizar otras peticiones al API",
                                                "example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo4MiwiZXhwIjoxNzU1MjQzODgwLCJyZXNpZGVuY2VfaWQiOjR9.eOc260-Sisa62tcjMlNpaaUmb6aZF3OJiTa1zesY0BU"
                                            },
                                            "token_expiration": {
                                                "type": "string",
                                                "format": "date-time",
                                                "description": "Fecha en que expira el token en el sistema",
                                                "example": "2025-08-15T07:44:40.116548Z"
                                            }
                                        }
                                    },
                                    "residence_id": {
                                        "type": "integer",
                                        "description": "Identificador de la residencia a la cual el usuario podrá acceder",
                                        "example": 4
                                    }
                                }
                            },
                            "examples": {
                                "success": {
                                    "summary": "Autenticación exitosa",
                                    "value": {
                                        "status": "success",
                                        "user": {
                                            "id": 82,
                                            "name": "Dr. Jorge Ramírez Jimenez",
                                            "login": "jorge_ramirez",
                                            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo4MiwiZXhwIjoxNzU1MjQzODgwLCJyZXNpZGVuY2VfaWQiOjR9.eOc260-Sisa62tcjMlNpaaUmb6aZF3OJiTa1zesY0BU",
                                            "token_expiration": "2025-08-15T07:44:40.116548Z"
                                        },
                                        "residence_id": 4
                                    }
                                },
                                "error": {
                                    "summary": "Autenticación fallida",
                                    "value": {
                                        "status": "error",
                                        "message": "Access Denied",
                                        "data": None,
                                        "pagination": None
                                    }
                                }
                            }
                        }
                    }
                },
                "400": {
                    "description": "Parámetros faltantes o inválidos",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "status": {
                                        "type": "string",
                                        "example": "error"
                                    },
                                    "message": {
                                        "type": "string",
                                        "example": "Parámetros requeridos faltantes"
                                    },
                                    "data": {
                                        "type": "null"
                                    },
                                    "pagination": {
                                        "type": "null"
                                    }
                                }
                            }
                        }
                    }
                },
                "401": {
                    "description": "Credenciales inválidas o acceso denegado",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "status": {
                                        "type": "string",
                                        "example": "error"
                                    },
                                    "message": {
                                        "type": "string",
                                        "example": "Access Denied"
                                    },
                                    "data": {
                                        "type": "null"
                                    },
                                    "pagination": {
                                        "type": "null"
                                    }
                                }
                            }
                        }
                    }
                },
                "500": {
                    "description": "Error interno del servidor",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "status": {
                                        "type": "string",
                                        "example": "error"
                                    },
                                    "message": {
                                        "type": "string",
                                        "example": "Error interno del servidor"
                                    },
                                    "data": {
                                        "type": "null"
                                    },
                                    "pagination": {
                                        "type": "null"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

    def doc_logout(self):
        """
        Documentación Swagger para el método logout
        """
        return {
            "tags": ["Autenticación"],
            "summary": "Cerrar sesión del usuario en el sistema",
            "description": """
            Endpoint para cerrar la sesión del usuario e invalidar el token JWT

            **Cabeceras requeridas:**
            - Content-Type: application/json
            - Authorization: Bearer <token_jwt>
            """,
            "consumes": ["application/json"],
            "produces": ["application/json"],
            "security": [{"bearerAuth": []}],
            "parameters": [
                {
                    "name": "Authorization",
                    "in": "header",
                    "required": True,
                    "description": "Token JWT de autenticación en formato 'Bearer {token}'",
                    "schema": {
                        "type": "string"
                    },
                    "example": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
                },
                {
                    "name": "Content-Type",
                    "in": "header",
                    "required": True,
                    "description": "Tipo de contenido debe ser application/json",
                    "schema": {
                        "type": "string",
                        "enum": ["application/json"]
                    },
                    "example": "application/json"
                },
            ],
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "description": "JSON vacío",
                            "example": {}
                        },
                        "example": {}
                    }
                }
            },
            "responses": {
                "200": {
                    "description": "Sesión cerrada exitosamente",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "status": {
                                        "type": "string",
                                        "description": "Indica si la consulta se ejecutó correctamente (success) o ocurrió un error (error)",
                                        "example": "success"
                                    },
                                    "message": {
                                        "type": "string",
                                        "description": "Mensaje correspondiente al estado de la ejecución de la petición",
                                        "example": "Sesión cerrada correctamente"
                                    },
                                    "data": {
                                        "type": "null",
                                        "description": "Siempre presente con valor None"
                                    },
                                    "pagination": {
                                        "type": "null",
                                        "description": "Siempre presente con valor None"
                                    }
                                }
                            },
                            "examples": {
                                "success": {
                                    "summary": "Logout exitoso",
                                    "value": {
                                        "status": "success",
                                        "message": "Sesión cerrada correctamente",
                                        "data": None,
                                        "pagination": None
                                    }
                                },
                                "error": {
                                    "summary": "Logout fallido",
                                    "value": {
                                        "status": "error",
                                        "message": "No se encontró el usuario",
                                        "data": None,
                                        "pagination": None
                                    }
                                }
                            }
                        }
                    }
                },
                "400": {
                    "description": "Token no proporcionado o inválido",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "status": {
                                        "type": "string",
                                        "example": "error"
                                    },
                                    "message": {
                                        "type": "string",
                                        "example": "Encabezado de autorización inválido"
                                    },
                                    "data": {
                                        "type": "null"
                                    },
                                    "pagination": {
                                        "type": "null"
                                    }
                                }
                            }
                        }
                    }
                },
                "401": {
                    "description": "Token expirado o no autorizado",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "status": {
                                        "type": "string",
                                        "example": "error"
                                    },
                                    "message": {
                                        "type": "string",
                                        "example": "Token expirado o inválido"
                                    },
                                    "data": {
                                        "type": "null"
                                    },
                                    "pagination": {
                                        "type": "null"
                                    }
                                }
                            }
                        }
                    }
                },
                "500": {
                    "description": "Error interno del servidor",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "status": {
                                        "type": "string",
                                        "example": "error"
                                    },
                                    "message": {
                                        "type": "string",
                                        "example": "Error interno del servidor"
                                    },
                                    "data": {
                                        "type": "null"
                                    },
                                    "pagination": {
                                        "type": "null"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

    def _get_jwt_expiration_datetime(self, env):
        """Obtener la fecha de expiración para el token JWT"""
        expiration_value = int(env['ir.config_parameter'].sudo().get_param(
            'jwt_token.expiration_value', 
            12
        ))
        expiration_unit = env['ir.config_parameter'].sudo().get_param(
            'jwt_token.expiration_unit', 
            'hours'
        )
        
        now = datetime.now()
        if expiration_unit == 'minutes':
            expiration = now + timedelta(minutes=expiration_value)
        elif expiration_unit == 'hours':
            expiration = now + timedelta(hours=expiration_value)
        else:  # 'days'
            expiration = now + timedelta(days=expiration_value)
        
        return expiration

    @http.route(
        "/api_serena/v1/login",
        type='json', 
        auth="none", 
        methods=['POST'], 
        csrf=False
    )
    def login(self, **post):
        """
        Login simple: siempre genera un nuevo token, reemplazando cualquier token anterior
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
            # Usar Registry directamente
            registry = Registry(current_db)
            with registry.cursor() as cr:
                env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
                
                # Crear el diccionario de credenciales
                credentials = {
                    'type': 'password',
                    'login': login,
                    'password': password
                }

                # Autenticar usuario
                uid = env['res.users'].authenticate(current_db, credentials, {})
                if not uid:
                    raise AccessDenied(_("Invalid credentials"))
                
                _logger.info(f"User authenticated with uid:{uid}")
                uid = uid.get('uid', 0)
                user = env['res.users'].sudo().browse(uid)
                
                if not user:
                   raise Exception("Usuario no encontrado")

                # Verificar acceso del usuario
                self._check_access_user_active(env, user.id)
                self._check_access_residences(env, user.id, residence_id)
                
                # Siempre generar nuevo token JWT (reemplaza cualquier token anterior)
                expiration_dt = self._get_jwt_expiration_datetime(env)
                
                # Crear payload
                payload = {
                    "user_id": user.id,
                    "login": user.login,
                    "exp": expiration_dt,
                    "residence_id": residence_id,
                    "iat": datetime.now()
                }
                
                # Generar nuevo token
                token = jwt.encode(
                    payload, 
                    BaseAPIController.SECRET_KEY, 
                    algorithm=BaseAPIController.ALGORITHM
                )
                
                # Guardar el nuevo token (reemplaza cualquier token anterior)
                user.sudo().write({
                    "jwt_token": token,
                    "token_expiration": expiration_dt
                })
                
                _logger.info(f"Nuevo token generado para usuario {user.login}")
                
                # Preparar respuesta
                answer = {
                    "status": "success",
                    "user": {
                        "id": user.id,
                        "name": user.name,
                        "login": user.login,
                        "token": token,
                        "token_expiration": self._convert_timezone(user, expiration_dt),
                    },
                    "residence_id": residence_id,
                    "message": "Sesión iniciada exitosamente"
                }
            
            _logger.info(f"Response: {answer}")
            return answer
            
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
        Logout simple: elimina el token del usuario sin verificar expiración
        """
        try:
            # Extraer token del encabezado Authorization
            auth_header = http.request.httprequest.headers.get('Authorization')
            if not auth_header or 'Bearer ' not in auth_header:
                raise Exception("Encabezado de autorización inválido")
            
            token = auth_header.split('Bearer ')[1].strip()
            current_db = request.env.cr.dbname
        
            answer = {}
            registry = Registry(current_db)
            with registry.cursor() as cr:
                env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
                
                # Buscar usuario por token (sin verificar expiración)
                users = env['res.users'].sudo().search([("jwt_token", "=", token)])
                
                if users:
                    # Invalidar token en base de datos
                    users.sudo().write({
                        "jwt_token": False,
                        "token_expiration": False
                    })
                    answer = {
                        "status": "success",
                        "message": "Sesión cerrada correctamente",
                        "data": None,
                        "pagination": None,
                    }
                else:
                    # Si no se encuentra por token exacto, intentar decodificar para obtener user_id
                    try:
                        # Intentar decodificar incluso si está expirado
                        payload = jwt.decode(
                            token, 
                            BaseAPIController.SECRET_KEY, 
                            algorithms=[BaseAPIController.ALGORITHM],
                            options={"verify_exp": False}  # No verificar expiración
                        )
                        user_id = payload.get('user_id')
                        
                        # Buscar usuario por ID y limpiar token
                        user = env['res.users'].sudo().browse(user_id)
                        if user:
                            user.sudo().write({
                                "jwt_token": False,
                                "token_expiration": False
                            })
                            answer = {
                                "status": "success",
                                "message": "Sesión cerrada correctamente (token expirado)",
                                "data": None,
                                "pagination": None,
                            }
                        else:
                            answer = {
                                "status": "error",
                                "message": "Usuario no encontrado en el sistema",
                                "data": None,
                                "pagination": None,
                            }
                    except:
                        # Token inválido o no se pudo decodificar
                        answer = {
                            "status": "error",
                            "message": "Token inválido",
                            "data": None,
                            "pagination": None,
                        }
            
            _logger.info(f"Response: {answer}")
            return answer
            
        except Exception as e:
            return self._handle_error(e)


    