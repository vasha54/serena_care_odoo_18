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

class HygieneController(BaseAPIController):

    def doc_register_hygiene(self):
        """
        Documentación Swagger para el método register_hygiene
        
        Returns:
            dict: Documentación Swagger para el endpoint de registrar alimentación
        """
        return {
            "tags": ["Higiene"],
            "summary": "Registrar higienización a un residente",
            "description": """
            Endpoint para registrar una higienización a un residente específico. 
            Requiere autenticación JWT válida.

            **Cabeceras requeridas:**
            - Content-Type: application/json
            - Authorization: Bearer <token_jwt>
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
                    "required": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "resident_id": {
                                "type": "integer",
                                "description": "Identificador del residente al cual se le va asignar la higienización",
                                "example": 6
                            },
                            "type_hygiene": {
                                "type": "integer",
                                "description": "Identificador del tipo de higiene",
                                "example": 8
                            },
                            "date": {
                                "type": "string",
                                "format": "date-time",
                                "description": "Fecha y hora que se hace la anotación en formato '%Y-%m-%d %H:%M:%S'",
                                "example": "2025-08-20 10:00:00"
                            },
                            "description": {
                                "type": "string",
                                "description": "Descripción detallada de la higienización",
                                "example": "Revisión general de salud y aseo"
                            }
                        },
                        "required": [
                            "resident_id",
                            "type_hygiene",
                            "date",
                            "description"
                        ]
                    }
                }
            ],
            "responses": {
                "200": {
                    "description": "Registro exitoso de registro de higienización",
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
                                        "example": "Registro creado existosamente"
                                    },
                                    "data": {
                                        "type": "object",
                                        "properties": {
                                            "id": {
                                                "type": "integer",
                                                "description": "Identificador del registro de higienización",
                                                "example": 15
                                            },
                                            "date": {
                                                "type": "string",
                                                "format": "date-time",
                                                "description": "Fecha y hora del registro en formato ISO",
                                                "example": "2025-08-20T10:00:00Z"
                                            },
                                            "user_id": {
                                                "type": "integer",
                                                "description": "Identificador del usuario que realizó el registro",
                                                "example": 73
                                            },
                                            "user_name": {
                                                "type": "string",
                                                "description": "Nombre del usuario que realizó el registro",
                                                "example": "Dra. Ana López"
                                            },
                                            "resident_id": {
                                                "type": "integer",
                                                "description": "Identificador del residente",
                                                "example": 6
                                            },
                                            "resident_name": {
                                                "type": "string",
                                                "description": "Nombre del residente",
                                                "example": "Guadalupe Hernández Díaz"
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
                },
                "401": {
                    "description": "Token inválido o sesión no iniciada",
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
                },
                "403": {
                    "description": "Acceso denegado - Residente no pertenece a la residencia del usuario",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "example": "error"
                            },
                            "message": {
                                "type": "string",
                                "example": "El residente no se encuentra en la residencia en el que usuario se autentico"
                            },
                            "data": {
                                "type": "null",
                                "example": None
                            }
                        }
                    }
                },
                "404": {
                    "description": "Residente no encontrado",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "example": "error"
                            },
                            "message": {
                                "type": "string",
                                "example": "Residente no encontrado"
                            },
                            "data": {
                                "type": "null",
                                "example": None
                            }
                        }
                    }
                },
                "500": {
                    "description": "Error interno del servidor",
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
            },
            "security": [
                {
                    "bearerAuth": []
                }
            ]
        }

    def doc_list_hygiene_this_resident_range(self):
        """
        Documentación Swagger para el método list_hygiene_this_resident_range
        
        Returns:
            dict: Documentación Swagger para el endpoint de listar la higienización de un residente por rango de fechas
        """
        return {
            "tags": ["Higiene"],
            "summary": "Listar la higienización de un residente en un rango de fechas",
            "description": """
            Endpoint para obtener toda la higienización de un residente específico
            dentro de un rango de fechas determinado. Requiere autenticación JWT válida.

            **Cabeceras requeridas:**
            - Content-Type: application/json
            - Authorization: Bearer <token_jwt>
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
                    "required": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "resident_id": {
                                "type": "integer",
                                "description": "Identificador del residente del cual se consultarán la higienización",
                                "example": 6
                            },
                            "date_start": {
                                "type": "string",
                                "format": "date",
                                "description": "Fecha de inicio del rango en formato YYYY-MM-DD",
                                "example": "2025-08-01"
                            },
                            "date_end": {
                                "type": "string",
                                "format": "date",
                                "description": "Fecha de fin del rango en formato YYYY-MM-DD",
                                "example": "2025-08-20"
                            }
                        },
                        "required": [
                            "resident_id",
                            "date_start",
                            "date_end"
                        ]
                    }
                }
            ],
            "responses": {
                "200": {
                    "description": "Lista de la higienización obtenida exitosamente",
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
                                        "example": "Datos obtenidos existosamente"
                                    },
                                    "data": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "id": {
                                                    "type": "integer",
                                                    "description": "Identificador del registro de la higienización",
                                                    "example": 15
                                                },
                                                "date": {
                                                    "type": "string",
                                                    "format": "date-time",
                                                    "description": "Fecha y hora del registro en formato YYYY-MM-DD HH:MM",
                                                    "example": "2025-08-20 10:00:00"
                                                },
                                                "user": {
                                                    "type": "object",
                                                    "description": "Objeto con información del usuario que creó la nota",
                                                    "properties": {
                                                        "id": {
                                                            "type": "integer",
                                                            "description": "Identificador del usuario",
                                                            "example": 73
                                                        },
                                                        "name": {
                                                            "type": "string",
                                                            "description": "Nombre del usuario",
                                                            "example": "Dra. Ana López"
                                                        }
                                                    }
                                                },
                                                "resident": {
                                                    "type": "object",
                                                    "description": "Objeto con información del residente",
                                                    "properties": {
                                                        "id": {
                                                            "type": "integer",
                                                            "description": "Identificador del residente",
                                                            "example": 6
                                                        },
                                                        "name": {
                                                            "type": "string",
                                                            "description": "Nombre del residente",
                                                            "example": "Guadalupe Hernández Díaz"
                                                        }
                                                    }
                                                },
                                                "htype": {
                                                    "type": "object",
                                                    "description": "Objeto con la información del tipo de higiene",
                                                    "properties": {
                                                        "id": {
                                                            "type": "integer",
                                                            "description": "Identificador del tipo de higiene",
                                                            "example": 6
                                                        },
                                                        "name": {
                                                            "type": "string",
                                                            "description": "Nombre del tipo de higiene",
                                                            "example": "Evacuar"
                                                        }
                                                        
                                                        
                                                    }
                                                },
                                                "etype": {
                                                    "type": "object",
                                                    "description": "Objeto con la información del tipo de evacuación en caso que  el tipo de higiene sea evacuación sino el valor será false",
                                                    "properties": {
                                                        "id": {
                                                            "type": "integer",
                                                            "description": "Identificador del tipo de evacuación",
                                                            "example": 2
                                                        },
                                                        "name": {
                                                            "type": "string",
                                                            "description": "Nombre del tipo de evacuación",
                                                            "example": "Nueces"
                                                        }
                                                    }
                                                },
                                                "description": {
                                                    "type": "string",
                                                    "description": "Descripción detallada de la higienización",
                                                    "example": "Revisión general de salud y actualización de medicamentos"
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "400": {
                    "description": "Parámetros faltantes, inválidos o rango de fechas incorrecto",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "example": "error"
                            },
                            "message": {
                                "type": "string",
                                "example": "Faltan parámetros requeridos o el rango de fecha es incorrecto"
                            },
                            "data": {
                                "type": "null",
                                "example": None
                            }
                        }
                    }
                },
                "401": {
                    "description": "Token inválido o sesión no iniciada",
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
                },
                "403": {
                    "description": "Acceso denegado - Residente no pertenece a la residencia del usuario",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "example": "error"
                            },
                            "message": {
                                "type": "string",
                                "example": "El residente no se encuentra en la residencia en el que usuario se autentico"
                            },
                            "data": {
                                "type": "null",
                                "example": None
                            }
                        }
                    }
                },
                "404": {
                    "description": "Residente no encontrado",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "example": "error"
                            },
                            "message": {
                                "type": "string",
                                "example": "Residente no encontrado"
                            },
                            "data": {
                                "type": "null",
                                "example": None
                            }
                        }
                    }
                },
                "500": {
                    "description": "Error interno del servidor",
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
            },
            "security": [
                {
                    "bearerAuth": []
                }
            ]
        }

    def doc_list_hygiene_this_resident_all(self):
        """
        Documentación Swagger para el método list_hygiene_this_resident_all
        
        Returns:
            dict: Documentación Swagger para el endpoint de listar todas la higienización de un residente
        """
        return {
            "tags": ["Higiene"],
            "summary": "Listar todas las higienización de un residente",
            "description": """
            Endpoint para obtener todos los registros de la higienización de un residente específico.
            Requiere autenticación JWT válida.

            **Cabeceras requeridas:**
            - Content-Type: application/json
            - Authorization: Bearer <token_jwt>
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
                    "required": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "resident_id": {
                                "type": "integer",
                                "description": "Identificador del residente del cual se consultarán todas la higienización",
                                "example": 6
                            }
                        },
                        "required": [
                            "resident_id"
                        ]
                    }
                }
            ],
            "responses": {
                "200": {
                    "description": "Lista completa de la alimentación obtenida exitosamente",
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
                                        "example": "Datos obtenidos existosamente"
                                    },
                                    "data": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "id": {
                                                    "type": "integer",
                                                    "description": "Identificador del registro de la higienización",
                                                    "example": 15
                                                },
                                                "date": {
                                                    "type": "string",
                                                    "format": "date-time",
                                                    "description": "Fecha y hora de registro de la higienización en formato YYYY-MM-DD HH:MM",
                                                    "example": "2025-08-20 10:00:00"
                                                },
                                                "user": {
                                                    "type": "object",
                                                    "description": "Objeto con información del usuario que creó la nota",
                                                    "properties": {
                                                        "id": {
                                                            "type": "integer",
                                                            "description": "Identificador del usuario",
                                                            "example": 73
                                                        },
                                                        "name": {
                                                            "type": "string",
                                                            "description": "Nombre del usuario",
                                                            "example": "Dra. Ana López"
                                                        }
                                                    }
                                                },
                                                "resident": {
                                                    "type": "object",
                                                    "description": "Objeto con información del residente",
                                                    "properties": {
                                                        "id": {
                                                            "type": "integer",
                                                            "description": "Identificador del residente",
                                                            "example": 6
                                                        },
                                                        "name": {
                                                            "type": "string",
                                                            "description": "Nombre del residente",
                                                            "example": "Guadalupe Hernández Díaz"
                                                        }
                                                    }
                                                },
                                                "htype": {
                                                    "type": "object",
                                                    "description": "Objeto con la información del nivel de la higienización",
                                                    "properties": {
                                                        "id": {
                                                            "type": "integer",
                                                            "description": "Identificador del tipo de higiene",
                                                            "example": 6
                                                        },
                                                        "name": {
                                                            "type": "string",
                                                            "description": "Nombre del tipo de higiene",
                                                            "example": "Higiene de sueño"
                                                        }
                                                    }
                                                },
                                                "etype": {
                                                    "type": "object",
                                                    "description": "Objeto con la información del tipo de evacuación en caso que  el tipo de higiene sea evacuación sino el valor será false",
                                                    "properties": {
                                                        "id": {
                                                            "type": "integer",
                                                            "description": "Identificador del tipo de evacuación",
                                                            "example": 2
                                                        },
                                                        "name": {
                                                            "type": "string",
                                                            "description": "Nombre del tipo de evacuación",
                                                            "example": "Nueces"
                                                        }
                                                    }
                                                },
                                                "description": {
                                                    "type": "string",
                                                    "description": "Descripción detallada de la higienización",
                                                    "example": "Revisión general de salud y actualización de higienización"
                                                }
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
                },
                "401": {
                    "description": "Token inválido o sesión no iniciada",
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
                },
                "403": {
                    "description": "Acceso denegado - Residente no pertenece a la residencia del usuario",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "example": "error"
                            },
                            "message": {
                                "type": "string",
                                "example": "El residente no se encuentra en la residencia en el que usuario se autentico"
                            },
                            "data": {
                                "type": "null",
                                "example": None
                            }
                        }
                    }
                },
                "404": {
                    "description": "Residente no encontrado",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "example": "error"
                            },
                            "message": {
                                "type": "string",
                                "example": "Residente no encontrado"
                            },
                            "data": {
                                "type": "null",
                                "example": None
                            }
                        }
                    }
                },
                "500": {
                    "description": "Error interno del servidor",
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
            },
            "security": [
                {
                    "bearerAuth": []
                }
            ]
        }
    
    @http.route(
        "/api_serena/v1/register_hygiene",
        type='json', 
        auth="none", 
        methods=['POST'], 
        csrf=False
    )
    def register_hygiene(self, **post):
        try:
            parameters = [
                'resident_id',
                'type_hygiene',
                'type_evacuation',
                'date',
                'description',
            ]
            token = self._get_token()
            payload = self._get_payload(token)
            data = self._get_json_data(request.httprequest.data)
            self._check_existence_parameters(parameters, data)
            
            current_db = request.env.cr.dbname
            user_id = payload['user_id']
            residence_id = payload['residence_id']
            resident_id = data['resident_id']
            type_hygiene_id = data['type_hygiene']
            type_evacuation_id =  data['type_evacuation']

            answer = {}
            # Usar Registry directamente como recomienda el warning
            registry = Registry(current_db)

            with registry.cursor() as cr:
                env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
                Hygiene = env['hygiene'].sudo()
                HygieneType = env['hygiene.type'].sudo()
                EvacuationType = env['evacuation.type'].sudo()
                ResUsers = env['res.users'].sudo()
                Resident = env['resident'].sudo()
                resident = None 
                user = None 
                # - Chequear que usuario tenga sessión activa
                user = ResUsers.browse(user_id)
            
                if not user:
                    raise AccessDenied("Usuario no encontrado")
                
                if not user.jwt_token or not user.token_expiration:
                    raise AccessDenied("El usuario no tiene sessión iniciada")

                # - Chequar que el usuario tenga los permisos para hacer
                if not self._check_user_permissions(user, 'hygiene', self.CAN_CREATE, env):
                    raise AccessDenied("El usuario no tiene los permisos para esta operación")

                # - Chequear que exista el residente 
                resident = Resident.browse(resident_id)

                if not resident:
                   raise AccessDenied("Residente no encontrado")
                
                # - Chequear que en la residencia donde trabaja el usuario
                # en esta sessión sea la misma que la del residente
                if resident and resident.residence_id.id != residence_id:
                   raise AccessDenied("El residente no se encuentra en la residencia en el que\
 usuario se autentico") 
                
                # - Chequear que exista el tipo de higiene
                hygiene_type = HygieneType.browse(type_hygiene_id)

                if not hygiene_type:
                   raise Exception("No existe tipo de higiene registrado en el sistema con ese identificador")

                if not hygiene_type.active:
                   raise Exception("El tipo de higiene no esta activo")
                
                date_adjust = self._adjust_timezone(user, data['date'])
                
                data = {
                        'resident_id': resident.id,
                        'user_id':user.id,
                        'description': data['description'],
                        'date': date_adjust,
                        'hygiene_type_id': data['type_hygiene']
                }

                xml_id_dict = hygiene_type.get_external_id()
                xml_id = xml_id_dict.get(hygiene_type.id)

                # Ahora comparamos el XML ID del objeto con el que esperamos
                # en este caso Evacuar
                if xml_id == 'sc_hygiene.htype_bow_hygiene':
                    evacuation_type = EvacuationType.browse(type_evacuation_id)
                    if not evacuation_type:
                        raise Exception("No existe tipo de evacuar registrado "
                                        "en el sistema con ese identificador")
                    if not evacuation_type.active:
                        raise Exception("El tipo de evacuación no esta activo")

                    data['evacuation_type_id'] = type_evacuation_id

                # Registrar la accion de higiene
                record_a = Hygiene.create(data)
                if record_a:
                    answer = {
                                "id": record_a.id,
                                "date": self._convert_to_iso(record_a.date),
                                "user_id": record_a.user_id.id,
                                "user_name": record_a.user_id.name,
                                "resident_id": record_a.resident_id.id,
                                "resident_name": record_a.resident_id.name,
                            }     

            answer = {
                        "status": "success", 
                        "message": "Registro creado existosamente",  
                        "data": answer
                    }     
            return answer
            # return Response( answer,headers={"Content-Type": "application/json"}, )
            
        except Exception as e:
            return self._handle_error(e)

    @http.route(
        "/api_serena/v1/list_hygiene_this_resident_range",
        type="json",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def list_hygiene_this_resident_range(self, **post):
        try:
            parameters = [
                "resident_id",
                "date_start",  # Formato YYYY-MM-DD
                "date_end",  # Formato YYYY-MM-DD
            ]
            token = self._get_token()
            payload = self._get_payload(token)
            data = self._get_json_data(request.httprequest.data)
            self._check_existence_parameters(parameters, data)

            current_db = request.env.cr.dbname
            user_id = payload["user_id"]
            residence_id = payload["residence_id"]
            resident_id = data["resident_id"]

            date_start_str = data["date_start"]
            date_end_str = data["date_end"]
            
            answer = {}
            # Usar Registry directamente como recomienda el warning
            registry = Registry(current_db)

            with registry.cursor() as cr:
                env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
                Hygiene = env["hygiene"].sudo()
                ResUsers = env["res.users"].sudo()
                Resident = env["resident"].sudo()
                resident = None
                user = None
                # - Chequear que usuario tenga sessión activa
                user = ResUsers.browse(user_id)

                if not user:
                    raise AccessDenied("Usuario no encontrado")

                if not user.jwt_token or not user.token_expiration:
                    raise AccessDenied("El usuario no tiene sessión iniciada")

                # - Chequar que el usuario tenga los permisos para hacer
                if not self._check_user_permissions(user, 'hygiene', self.CAN_READ, env):
                    raise AccessDenied("El usuario no tiene los permisos para esta operación")

                # - Chequear que exista el residente
                resident = Resident.browse(resident_id)

                if not resident:
                    raise AccessDenied("Residente no encontrado")

                # - Chequear que en la residencia donde trabaja el usuario
                # en esta sessión sea la misma que la del residente
                if resident and resident.residence_id.id != residence_id:
                    raise AccessDenied(
                        "El residente no se encuentra en la residencia en el \
que usuario se autentico"
                    )

                date_start_str = self._adjust_timezone(user,date_start_str)
                date_end_str = self._adjust_timezone(user,date_end_str)    
                date_start = parser.parse(date_start_str)
                date_end = parser.parse(date_end_str)
                date_start = datetime.combine(date_start, time.min)
                date_end = datetime.combine(date_end, time.max)

                if date_start > date_end:
                    raise Exception("El rango de fecha seleccionado es incorrecto")

                # Listar todas la notas de enfermería del residente
                answer = []
                records = Hygiene.search_read(
                    domain=[
                        ("resident_id", "=", resident_id),
                        ("date", ">=", date_start),
                        ("date", "<=", date_end),
                    ],
                    fields=[
                        "id",
                        "date",
                        "resident",
                        "user",
                        "description",
                        "htype",
                        "etype",
                    ],
                    order="date DESC",
                )

                if records:
                    for wb in records:
                        answer.append(
                            {
                                "date": self._convert_timezone(user,wb["date"])
                                if wb["date"]
                                else "",
                                "user": wb["user"],
                                "resident": wb["resident"],
                                "id": wb["id"],
                                "description": wb["description"], 
                                "htype": wb["htype"],
                                "etype": wb["etype"]
                            }
                        )

            answer = {
                    "status": "success",
                    "message": "Datos obtenidos existosamente",
                    "data": answer,
                }
            return answer
        except Exception as e:
            return self._handle_error(e)

    @http.route(
        "/api_serena/v1/list_hygiene_this_resident_all",
        type="json",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def list_hygiene_this_resident_all(self, **post):
        try:
            parameters = [
                "resident_id",
            ]
            token = self._get_token()
            payload = self._get_payload(token)
            data = self._get_json_data(request.httprequest.data)
            self._check_existence_parameters(parameters, data)

            current_db = request.env.cr.dbname
            user_id = payload["user_id"]
            residence_id = payload["residence_id"]
            resident_id = data["resident_id"]

            answer = {}
            # Usar Registry directamente como recomienda el warning
            registry = Registry(current_db)

            with registry.cursor() as cr:
                env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
                Hygiene = env["hygiene"].sudo()
                ResUsers = env["res.users"].sudo()
                Resident = env["resident"].sudo()
                resident = None
                user = None
                # - Chequear que usuario tenga sessión activa
                user = ResUsers.browse(user_id)

                if not user:
                    raise AccessDenied("Usuario no encontrado")

                if not user.jwt_token or not user.token_expiration:
                    raise AccessDenied("El usuario no tiene sessión iniciada")

                # - Chequar que el usuario tenga los permisos para hacer
                if not self._check_user_permissions(user, 'hygiene', self.CAN_READ, env):
                    raise AccessDenied("El usuario no tiene los permisos para esta operación")

                # - Chequear que exista el residente
                resident = Resident.browse(resident_id)

                if not resident:
                    raise AccessDenied("Residente no encontrado")

                # - Chequear que en la residencia donde trabaja el usuario
                # en esta sessión sea la misma que la del residente
                if resident and resident.residence_id.id != residence_id:
                    raise AccessDenied(
                        "El residente no se encuentra en la residencia en el \
que usuario se autentico"
                    )

                # Listar todas la notas de Enfermería del residente
                answer = []
                records_wb = Hygiene.search_read(
                    domain=[
                        ("resident_id", "=", resident_id),
                    ],
                    fields=[
                        "id",
                        "date",
                        "resident",
                        "user",
                        "description",
                        "htype",
                        "etype",
                    ],
                    order="date DESC",
                )

                if records_wb:
                    for wb in records_wb:
                        answer.append(
                            {
                                "date": self._convert_timezone(user,wb["date"])
                                if wb["date"]
                                else "",
                                "user": wb["user"],
                                "resident": wb["resident"],
                                "id": wb["id"],
                                "description": wb["description"], 
                                "htype": wb["htype"],
                                "etype": wb["etype"],
                            }
                        )

            answer = {
                    "status": "success",
                    "message": "Datos obtenidos existosamente",
                    "data": answer,
                }
            return answer
        except Exception as e:
            return self._handle_error(e)

   
