import base64
import json
import jwt
import logging
import odoo

from odoo import _, http
from odoo.http import Response, request
from odoo.exceptions import AccessDenied
from odoo.modules.registry import Registry

from dateutil import parser
from datetime import datetime, time

from ..controllers_base import BaseAPIController

_logger = logging.getLogger(__name__)

class UserController(BaseAPIController):

    def doc_get_profile_this_user(self):
        """
        Documentación Swagger para el método get_profile_this_user

        Returns:
            dict: Documentación Swagger para el endpoint de obtener perfil de usuario
        """
        return {
            "tags": ["Usuarios"],
            "summary": "Obtener perfil del usuario actual",
            "description": """
            Endpoint para obtener el perfil completo del usuario autenticado.
            Requiere autenticación JWT válida que contiene el user_id y residence_id.

            **Cabeceras requeridas:**
            - Content-Type: application/json
            - Authorization: Bearer <token_jwt>

            **Notas:**
            - La dirección de contacto se construye automáticamente si no está definida
            - La imagen del usuario se devuelve como URL accesible
            - Incluye información completa de la residencia asociada al usuario
            - La dirección de la residencia también se construye automáticamente
            """,
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
                {
                    "name": "body",
                    "in": "body",
                    "required": False,
                    "description": "Este endpoint no requiere parámetros en el body, solo el token JWT en el header",
                    "schema": {
                        "type": "object",
                        "properties": {}
                    }
                }
            ],
            "responses": {
                "200": {
                    "description": "Perfil de usuario obtenido exitosamente",
                    "headers": {
                        "Content-Type": {
                            "type": "string",
                            "description": "Tipo de contenido de la respuesta"
                        }
                    },
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "status": {
                                        "type": "string",
                                        "example": "success"
                                    },
                                    "message": {
                                        "type": "string",
                                        "example": "Perfil obtenido existosamente"
                                    },
                                    "data": {
                                        "type": "object",
                                        "properties": {
                                            "id": {
                                                "type": "integer",
                                                "description": "Identificador único del usuario",
                                                "example": 10
                                            },
                                            "name": {
                                                "type": "string",
                                                "description": "Nombre completo del usuario",
                                                "example": "Dr. Carlos Ruiz"
                                            },
                                            "image_1920": {
                                                "type": "boolean",
                                                "description": "Indica si el usuario tiene imagen de perfil",
                                                "example": True
                                            },
                                            "login": {
                                                "type": "string",
                                                "description": "Nombre de usuario para login",
                                                "example": "carlos_ruiz"
                                            },
                                            "groups_data": {
                                                "type": "array",
                                                "description": "Lista de grupos y permisos del usuario",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "id": {
                                                            "type": "integer",
                                                            "description": "ID del grupo",
                                                            "example": 29
                                                        },
                                                        "name": {
                                                            "type": "string",
                                                            "description": "Nombre del grupo",
                                                            "example": "Gerente Salud"
                                                        }
                                                    }
                                                }
                                            },
                                            "email": {
                                                "type": "string",
                                                "format": "email",
                                                "description": "Correo electrónico del usuario",
                                                "example": "carlos.ruiz@serenacare.mx"
                                            },
                                            "mobile": {
                                                "type": ["string", "boolean"],
                                                "description": "Número de teléfono móvil",
                                                "example": False
                                            },
                                            "phone": {
                                                "type": "string",
                                                "description": "Número de teléfono fijo",
                                                "example": "+52 415 222 3333"
                                            },
                                            "login_date": {
                                                "type": "string",
                                                "format": "date-time",
                                                "description": "Fecha y hora del último login",
                                                "example": "2026-01-02 19:55:56"
                                            },
                                            "state": {
                                                "type": "string",
                                                "description": "Estado del usuario (active, inactive)",
                                                "example": "active"
                                            },
                                            "contact_address": {
                                                "type": "string",
                                                "description": "Dirección completa formateada del usuario",
                                                "example": "Calle Maceo. Entre Acana y Lopez Coloma. Número 54. Ciudad Dfg. Municipio Escobedo. Estado Coahuila de Zaragoza."
                                            },
                                            "city": {
                                                "type": "string",
                                                "description": "Ciudad del usuario",
                                                "example": "Dfg"
                                            },
                                            "zip": {
                                                "type": "string",
                                                "description": "Código postal",
                                                "example": "1400"
                                            },
                                            "street": {
                                                "type": "string",
                                                "description": "Calle principal",
                                                "example": "Maceo"
                                            },
                                            "street2": {
                                                "type": "string",
                                                "description": "Primera calle de referencia",
                                                "example": "Acana"
                                            },
                                            "street3": {
                                                "type": "string",
                                                "description": "Segunda calle de referencia",
                                                "example": "Lopez Coloma"
                                            },
                                            "street_number": {
                                                "type": "string",
                                                "description": "Número de la calle",
                                                "example": "54"
                                            },
                                            "country": {
                                                "type": "object",
                                                "description": "País del usuario",
                                                "properties": {
                                                    "id": {
                                                        "type": "integer",
                                                        "example": 156
                                                    },
                                                    "name": {
                                                        "type": "string",
                                                        "example": "Mexico"
                                                    }
                                                }
                                            },
                                            "province": {
                                                "type": "object",
                                                "description": "Estado/provincia del usuario",
                                                "properties": {
                                                    "id": {
                                                        "type": "integer",
                                                        "example": 5
                                                    },
                                                    "name": {
                                                        "type": "string",
                                                        "example": "Coahuila de Zaragoza"
                                                    }
                                                }
                                            },
                                            "municipality": {
                                                "type": "object",
                                                "description": "Municipio del usuario",
                                                "properties": {
                                                    "id": {
                                                        "type": "integer",
                                                        "example": 250
                                                    },
                                                    "name": {
                                                        "type": "string",
                                                        "example": "Escobedo"
                                                    }
                                                }
                                            },
                                            "residence": {
                                                "type": "object",
                                                "description": "Información completa de la residencia asociada al usuario",
                                                "properties": {
                                                    "id": {
                                                        "type": "integer",
                                                        "description": "ID de la residencia",
                                                        "example": 1
                                                    },
                                                    "name": {
                                                        "type": "string",
                                                        "description": "Nombre de la residencia",
                                                        "example": "Casa Serena Polanco"
                                                    },
                                                    "contact_address": {
                                                        "type": "string",
                                                        "description": "Dirección oficial de la residencia",
                                                        "example": "Calle Av. Presidente Masaryk 123. Ciudad Ciudad de México. Estado Ciudad de México."
                                                    },
                                                    "city": {
                                                        "type": "string",
                                                        "description": "Ciudad de la residencia",
                                                        "example": "Ciudad de México"
                                                    },
                                                    "zip": {
                                                        "type": ["string", "boolean"],
                                                        "description": "Código postal de la residencia",
                                                        "example": False
                                                    },
                                                    "street": {
                                                        "type": "string",
                                                        "description": "Calle principal de la residencia",
                                                        "example": "Av. Presidente Masaryk 123"
                                                    },
                                                    "street2": {
                                                        "type": ["string", "boolean"],
                                                        "description": "Primera referencia de la residencia",
                                                        "example": "Col. Polanco"
                                                    },
                                                    "street3": {
                                                        "type": ["string", "boolean"],
                                                        "description": "Segunda referencia de la residencia",
                                                        "example": False
                                                    },
                                                    "street_number": {
                                                        "type": ["string", "boolean"],
                                                        "description": "Número de la residencia",
                                                        "example": False
                                                    },
                                                    "email": {
                                                        "type": "string",
                                                        "format": "email",
                                                        "description": "Email de la residencia",
                                                        "example": "polanco@serenacare.mx"
                                                    },
                                                    "mobile": {
                                                        "type": ["string", "boolean"],
                                                        "description": "Teléfono móvil de la residencia",
                                                        "example": False
                                                    },
                                                    "phone": {
                                                        "type": "string",
                                                        "description": "Teléfono fijo de la residencia",
                                                        "example": "+52 55 1234 5678"
                                                    },
                                                    "address": {
                                                        "type": "string",
                                                        "description": "Dirección completa formateada de la residencia",
                                                        "example": "Calle Av. Presidente Masaryk 123. Entre Col. Polanco y False. Ciudad Ciudad de México."
                                                    }
                                                }
                                            },
                                            "image_1920_url": {
                                                "type": "string",
                                                "format": "uri",
                                                "description": "URL pública para acceder a la imagen del usuario",
                                                "example": "http://localhost:8069/public/image/user/10"
                                            }
                                        }
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
                                        "example": "Faltan parámetros requeridos"
                                    },
                                    "data": {
                                        "type": "null",
                                        "example": None
                                    }
                                }
                            }
                        }
                    }
                },
                "401": {
                    "description": "Token inválido o sesión no iniciada",
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
                                        "example": "El usuario no tiene sessión iniciada"
                                    },
                                    "data": {
                                        "type": "null",
                                        "example": None
                                    }
                                }
                            }
                        }
                    }
                },
                "404": {
                    "description": "Usuario no encontrado",
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
                                        "example": "Usuario no encontrado"
                                    },
                                    "data": {
                                        "type": "null",
                                        "example": None
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
                                        "type": "null",
                                        "example": None
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "security": [
                {
                    "bearerAuth": []
                }
            ]
        }

    def _build_address(self, _data):
        address_complete = ''
        if _data.get("street"):
            address_complete = f"Calle {_data.get('street')}. "
        if _data.get("street2") and _data.get("street2"):
            address_complete += f"Entre {_data.get('street2')} y " \
                                f"{_data.get('street3')}. "
        if _data.get('street_number'):
            address_complete += f"Número {_data.get('street_number')}. "
        if _data.get('city'):
            address_complete += f"Ciudad {_data.get('city')}. "
        if _data.get('municipality'):
            address_complete += f"Municipio " \
                                f"{_data.get('municipality').get('name')}. "
        if _data.get('province'):
            address_complete += f"Estado {_data.get('province').get('name')}."
        return address_complete

    @http.route(
        "/api_serena/v1/profile_user",
        type='json',
        auth="none",
        methods=['POST'],
        csrf=False
    )
    def get_profile_this_user(self, **post):
        try:
            parameters = []
            token = self._get_token()
            payload = self._get_payload(token)
            data = self._get_json_data(request.httprequest.data)
            self._check_existence_parameters(parameters, data)

            current_db = request.env.cr.dbname
            user_id = payload['user_id']
            residence_id = payload['residence_id']
            answer = {}
            # Usar Registry directamente como recomienda el warning
            registry = Registry(current_db)

            with registry.cursor() as cr:
                env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
                ResUsers = env['res.users'].sudo()
                ResidenceHouse = env['residence_house'].sudo()

                base_url = (
                        env["ir.config_parameter"].sudo().get_param("web.base.url")
                    )
                users = ResUsers.search_read(
                        domain=[("id", "=", user_id)],
                        fields=[
                            "id",
                            "name",
                            "image_1920",
                            "login",
                            "groups_data",
                            "email",
                            "mobile",
                            "phone",
                            "login_date",
                            "state",
                            "contact_address",
                            "city",
                            "zip",
                            "street",
                            "street2",
                            "street3",
                            "street_number",
                            "country",
                            "province",
                            "municipality",
                        ],
                        limit=1,
                    )
                residence = False
                residences = ResidenceHouse.search_read(
                        domain=[("id", "=", residence_id)],
                        fields=[
                            "id",
                            "name",
                            "contact_address",
                            "city",
                            "zip",
                            "street",
                            "street2",
                            "street3",
                            "street_number",
                            "email",
                            "mobile",
                            "phone",
                            ],
                        limit=1
                )
                if residences:
                    residence = residences[0]

                if users:
                    user = users[0]
                    user["residence"] = residence
                    if user:
                        answer = user
                        if answer.get("image_1920"):
                            answer["image_1920"] = True
                            answer[
                                "image_1920_url"
                            ] = f"{base_url}/public/image/user/{answer['id']}"
                        else:
                            answer["image_1920"] = False
                            answer["image_1920_url"] = None

                        answer['contact_address'] = answer['contact_address']\
                            if answer['contact_address'] else \
                            self._build_address(answer)
                        
                        if residence:
                            answer['residence'] = residence
                            answer['residence']['address']= self._build_address(residence)
                            
                        
            answer = {
                        "status": "success",
                        "message": "Perfil obtenido existosamente",
                        "data": answer
                    }
            _logger.info(f"Response: {answer}")
            return answer
        except Exception as e:
            return self._handle_error(e)
