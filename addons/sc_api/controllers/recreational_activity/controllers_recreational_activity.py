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

class ActivityRecreationalAPIController(BaseAPIController):

    def doc_list_activity_recreational_this_resident_range(self):
        return {
            "tags": ["Actividades Recreativas"],
            "summary": "Listar actividades recreativas de un residente en un rango de fechas",
            "description": """
            Endpoint para obtener todas las actividades recreativas de un residente específico 
            dentro de un rango de fechas determinado.
            
            **Cabeceras requeridas:**
            - Content-Type: application/json
            - Authorization: Bearer <token_jwt>
            """,
            "consumes": ["application/json"],
            "produces": ["application/json"],
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
                    "description": "Parámetros para filtrar las actividades",
                    "schema": {
                        "type": "object",
                        "required": [
                            "resident_id",
                            "date_start",
                            "date_end"
                        ],
                        "properties": {
                            "resident_id": {
                                "type": "integer",
                                "description": "ID del residente del cual se desean consultar las actividades",
                                "example": 4
                            },
                            "date_start": {
                                "type": "string",
                                "format": "date",
                                "description": "Fecha de inicio del rango (formato: YYYY-MM-DD)",
                                "example": "2025-10-01"
                            },
                            "date_end": {
                                "type": "string",
                                "format": "date",
                                "description": "Fecha de fin del rango (formato: YYYY-MM-DD)",
                                "example": "2025-10-31"
                            }
                        }
                    }
                }
            ],
            "responses": {
                "200": {
                    "description": "Lista de actividades recreativas obtenida exitosamente",
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
                                                    "description": "ID del registro de participación en la actividad",
                                                    "example": 4
                                                },
                                                "date_execution": {
                                                    "type": "string",
                                                    "format": "date-time",
                                                    "description": "Fecha y hora de ejecución de la actividad",
                                                    "example": "2025-10-13 10:30"
                                                },
                                                "user": {
                                                    "type": "object",
                                                    "properties": {
                                                        "id": {
                                                            "type": "integer",
                                                            "description": "ID del usuario que registró la actividad",
                                                            "example": 10
                                                        },
                                                        "name": {
                                                            "type": "string",
                                                            "description": "Nombre del usuario que registró la actividad",
                                                            "example": "Dr. Carlos Ruiz"
                                                        }
                                                    }
                                                },
                                                "resident": {
                                                    "type": "object",
                                                    "properties": {
                                                        "id": {
                                                            "type": "integer",
                                                            "description": "ID del residente que participó",
                                                            "example": 4
                                                        },
                                                        "name": {
                                                            "type": "string",
                                                            "description": "Nombre del residente que participó",
                                                            "example": "Ana Flores Ramírez"
                                                        }
                                                    }
                                                },
                                                "description": {
                                                    "type": "string",
                                                    "description": "Descripción detallada de la actividad realizada",
                                                    "example": "Sesión de yoga matutina en el jardín principal"
                                                },
                                                "activity_type": {
                                                    "type": "object",
                                                    "properties": {
                                                        "id": {
                                                            "type": "integer",
                                                            "description": "ID del tipo de actividad",
                                                            "example": 2
                                                        },
                                                        "name": {
                                                            "type": "string",
                                                            "description": "Nombre del tipo de actividad",
                                                            "example": "Visitas"
                                                        }
                                                    }
                                                },
                                                "activity": {
                                                    "type": "object",
                                                    "properties": {
                                                        "id": {
                                                            "type": "integer",
                                                            "description": "ID de la actividad recreativa principal",
                                                            "example": 4
                                                        }
                                                    }
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
                    "description": "Error en los parámetros de entrada o rango de fechas inválido",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "example": "error"
                            },
                            "message": {
                                "type": "string",
                                "example": "El rango de fecha seleccionado es incorrecto"
                            }
                        }
                    }
                },
                "401": {
                    "description": "Error de autenticación - Token inválido, expirado o cabecera Authorization faltante",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "example": "error"
                            },
                            "message": {
                                "type": "string",
                                "example": "Token inválido o expirado"
                            }
                        }
                    }
                },
                "403": {
                    "description": "Usuario sin permisos para realizar la operación o residente no pertenece a la residencia",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "example": "error"
                            },
                            "message": {
                                "type": "string",
                                "example": "El residente no se encuentra en la residencia en la que usuario se autenticó"
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
                            }
                        }
                    }
                },
                "415": {
                    "description": "Tipo de medio no soportado - Content-Type incorrecto",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "example": "error"
                            },
                            "message": {
                                "type": "string",
                                "example": "Content-Type debe ser application/json"
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
                            }
                        }
                    }
                }
            },
            "security": [
                {
                    "BearerAuth": []
                }
            ]
        }

    def doc_list_activity_recreational_this_resident_all(self):
        return {
            "tags": ["Actividades Recreativas"],
            "summary": "Listar todas las actividades recreativas de un residente",
            "description": """
            Endpoint para obtener todas las actividades recreativas de un residente específico 
            sin filtro de fechas.
            
            **Cabeceras requeridas:**
            - Content-Type: application/json
            - Authorization: Bearer <token_jwt>
            """,
            "consumes": ["application/json"],
            "produces": ["application/json"],
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
                    "description": "Parámetros para obtener las actividades",
                    "schema": {
                        "type": "object",
                        "required": [
                            "resident_id"
                        ],
                        "properties": {
                            "resident_id": {
                                "type": "integer",
                                "description": "ID del residente del cual se desean consultar las actividades",
                                "example": 4
                            }
                        }
                    }
                }
            ],
            "responses": {
                "200": {
                    "description": "Lista completa de actividades recreativas obtenida exitosamente",
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
                                                    "description": "ID del registro de participación en la actividad",
                                                    "example": 4
                                                },
                                                "date_execution": {
                                                    "type": "string",
                                                    "format": "date-time",
                                                    "description": "Fecha y hora de ejecución de la actividad",
                                                    "example": "2025-10-13 10:30"
                                                },
                                                "user": {
                                                    "type": "object",
                                                    "properties": {
                                                        "id": {
                                                            "type": "integer",
                                                            "description": "ID del usuario que registró la actividad",
                                                            "example": 10
                                                        },
                                                        "name": {
                                                            "type": "string",
                                                            "description": "Nombre del usuario que registró la actividad",
                                                            "example": "Dr. Carlos Ruiz"
                                                        }
                                                    }
                                                },
                                                "resident": {
                                                    "type": "object",
                                                    "properties": {
                                                        "id": {
                                                            "type": "integer",
                                                            "description": "ID del residente que participó",
                                                            "example": 4
                                                        },
                                                        "name": {
                                                            "type": "string",
                                                            "description": "Nombre del residente que participó",
                                                            "example": "Ana Flores Ramírez"
                                                        }
                                                    }
                                                },
                                                "description": {
                                                    "type": "string",
                                                    "description": "Descripción detallada de la actividad realizada",
                                                    "example": "Sesión de yoga matutina en el jardín principal"
                                                },
                                                "activity_type": {
                                                    "type": "object",
                                                    "properties": {
                                                        "id": {
                                                            "type": "integer",
                                                            "description": "ID del tipo de actividad",
                                                            "example": 2
                                                        },
                                                        "name": {
                                                            "type": "string",
                                                            "description": "Nombre del tipo de actividad",
                                                            "example": "Visitas"
                                                        }
                                                    }
                                                },
                                                "activity": {
                                                    "type": "object",
                                                    "properties": {
                                                        "id": {
                                                            "type": "integer",
                                                            "description": "ID de la actividad recreativa principal",
                                                            "example": 4
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "401": {
                    "description": "Error de autenticación - Token inválido, expirado o cabecera Authorization faltante",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "example": "error"
                            },
                            "message": {
                                "type": "string",
                                "example": "Token inválido o expirado"
                            }
                        }
                    }
                },
                "403": {
                    "description": "Usuario sin permisos para realizar la operación o residente no pertenece a la residencia",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "example": "error"
                            },
                            "message": {
                                "type": "string",
                                "example": "El residente no se encuentra en la residencia en la que usuario se autenticó"
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
                            }
                        }
                    }
                },
                "415": {
                    "description": "Tipo de medio no soportado - Content-Type incorrecto",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "example": "error"
                            },
                            "message": {
                                "type": "string",
                                "example": "Content-Type debe ser application/json"
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
                            }
                        }
                    }
                }
            },
            "security": [
                {
                    "BearerAuth": []
                }
            ]
        }

    def doc_register_activity_recreational(self):
        return {
            "tags": ["Actividades Recreativas"],
            "summary": "Registrar una actividad recreativa para residentes",
            "description": """
            Endpoint para registrar la participación de uno o más residentes en una actividad recreativa.
            Permite asociar múltiples residentes a una actividad específica con fecha y descripción.
            
            **Cabeceras requeridas:**
            - Content-Type: application/json
            - Authorization: Bearer <token_jwt>
            """,
            "consumes": ["application/json"],
            "produces": ["application/json"],
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
                    "description": "Datos de la actividad recreativa a registrar",
                    "schema": {
                        "type": "object",
                        "required": [
                            "resident_ids",
                            "activity_type_id", 
                            "description",
                            "date"
                        ],
                        "properties": {
                            "resident_ids": {
                                "type": "array",
                                "items": {
                                    "type": "integer"
                                },
                                "description": "Lista de IDs de residentes que participaron en la actividad",
                                "example": [101, 102, 103]
                            },
                            "activity_type_id": {
                                "type": "integer",
                                "description": "ID del tipo de actividad recreativa (debe existir en nomenclatura)",
                                "example": 5
                            },
                            "description": {
                                "type": "string",
                                "description": "Descripción detallada de la actividad realizada",
                                "example": "Sesión de yoga matutina en el jardín principal"
                            },
                            "date": {
                                "type": "string",
                                "format": "date-time",
                                "description": "Fecha y hora que se hace la anotación en formato '%Y-%m-%d %H:%M:%S'",
                                "example": "2025-08-20 10:00:00",
                            }
                        }
                    }
                }
            ],
            "responses": {
                "200": {
                    "description": "Registro exitoso de la actividad recreativa",
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
                                        "example": "Registro creado exitosamente"
                                    },
                                    "data": {
                                        "type": "object",
                                        "properties": {
                                            "id": {
                                                "type": "integer",
                                                "description": "ID del registro de actividad creado",
                                                "example": 45
                                            },
                                            "date": {
                                                "type": "string",
                                                "format": "date-time",
                                                "description": "Fecha de creación del registro",
                                                "example": "2023-11-15T11:45:30Z"
                                            },
                                            "user_id": {
                                                "type": "integer",
                                                "description": "ID del usuario que realizó el registro",
                                                "example": 8
                                            },
                                            "user_name": {
                                                "type": "string",
                                                "description": "Nombre del usuario que realizó el registro",
                                                "example": "Ana García"
                                            },
                                            "resident_associated": {
                                                "type": "array",
                                                "items": {
                                                    "type": "integer"
                                                },
                                                "description": "IDs de residentes correctamente asociados a la actividad",
                                                "example": [101, 102]
                                            },
                                            "resident_not_associated": {
                                                "type": "array",
                                                "items": {
                                                    "type": "integer"
                                                },
                                                "description": "IDs de residentes que no pudieron asociarse (no pertenecen a la residencia)",
                                                "example": [103]
                                            },
                                            "resident_not_found": {
                                                "type": "array",
                                                "items": {
                                                    "type": "integer"
                                                },
                                                "description": "IDs de residentes que no existen en el sistema",
                                                "example": [105, 107]
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    },
                },
                "400": {
                    "description": "Error en los parámetros de entrada o cabeceras incorrectas",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "example": "error"
                            },
                            "message": {
                                "type": "string",
                                "example": "Parámetros requeridos: resident_ids, activity_type_id, description, date_execution"
                            },
                            "data": {
                                "type": "object",
                                "properties": {
                                    "parameters": {
                                        "type": "array",
                                        "items": {
                                            "type": "string"
                                        },
                                        "example": ["resident_ids", "activity_type_id"]
                                    }
                                }
                            }
                        }
                    }
                },
                "401": {
                    "description": "Error de autenticación - Token inválido, expirado o cabecera Authorization faltante",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "example": "error"
                            },
                            "message": {
                                "type": "string",
                                "example": "Token inválido o expirado"
                            }
                        }
                    }
                },
                "403": {
                    "description": "Usuario sin permisos para realizar la operación",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "example": "error"
                            },
                            "message": {
                                "type": "string",
                                "example": "Usuario no tiene permisos para registrar actividades"
                            }
                        }
                    }
                },
                "404": {
                    "description": "Recurso no encontrado",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "example": "error"
                            },
                            "message": {
                                "type": "string",
                                "example": "El tipo de actividad no se encuentra en el sistema"
                            }
                        }
                    }
                },
                "415": {
                    "description": "Tipo de medio no soportado - Content-Type incorrecto",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "example": "error"
                            },
                            "message": {
                                "type": "string",
                                "example": "Content-Type debe ser application/json"
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
                            }
                        }
                    }
                }
            },
            "security": [
                {
                    "BearerAuth": []
                }
            ]
        }


    @http.route(
        "/api_serena/v1/register_activity_recreational",
        type='json', 
        auth="none", 
        methods=['POST'], 
        csrf=False
    )
    def register_activity_recreational(self, **post):
        try:
            parameters = [
                'resident_ids',
                'activity_type_id',
                'description',
                'date',
            ]
            token = self._get_token()
            payload = self._get_payload(token)
            data = self._get_json_data(request.httprequest.data)
            self._check_existence_parameters(parameters, data)
            
            current_db = request.env.cr.dbname
            user_id = payload['user_id']
            residence_id = payload['residence_id']
            resident_ids = data['resident_ids']
            activity_type_id = data['activity_type_id']
            resident_ids = list(dict.fromkeys(resident_ids))

            answer = {}
            # Usar Registry directamente como recomienda el warning
            registry = Registry(current_db)

            with registry.cursor() as cr:
                env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
                RecreationalActivity = env['recreational.activity'].sudo()
                NomenclatureActivityType = env['nomenclature.activity.type'].sudo()
                ResUsers = env['res.users'].sudo()
                Resident = env['resident'].sudo()
                RelResidentRecreationActivity = env['resident.recreation.activity.rel'].sudo()
                residents = []
                user = None 
                # - Chequear que usuario tenga sessión activa
                user = ResUsers.browse(user_id)
                if not user:
                    raise AccessDenied("Usuario no encontrado")
                
                if not user.jwt_token or not user.token_expiration:
                    raise AccessDenied("El usuario no tiene sessión iniciada")

                nomen_activity_type = NomenclatureActivityType.search(
                        domain = [('id','=',activity_type_id),('active','=',True)],
                        limit=1
                    )       

                if not nomen_activity_type:
                    raise Exception("El tipo de actividad no se encuentra en el sistema o "
                                    "esta deshabilitado en estos momentos")
  
                # - Chequar que el usuario tenga los permisos para hacer
                if not self._check_user_permissions(user, 'recreational.activity', self.CAN_CREATE, env):
                    raise AccessDenied("El usuario no tiene los permisos para esta operación")
                
                # - Chequar que el usuario tenga los permisos para hacer
                if not self._check_user_permissions(user, 'resident.recreation.activity.rel', self.CAN_CREATE, env):
                    raise AccessDenied("El usuario no tiene los permisos para esta operación")
                
                # Dado los identificadores de los residentes determinar cuales no existen y cuales
                # si   
                residents = Resident.search( 
                    domain=[
                                ('id','in',resident_ids),
                                ('active','=',True),
                                ('is_deleted','=',False)
                            ])
                resident_succes = []
                resident_fails = []
                resident_not_founds = resident_ids
                for resident in residents:
                    resident_id = resident.id
                    resident_not_founds.remove(resident_id) 
                    if resident.residence_id.id == residence_id:
                       resident_succes.append(resident)
                    else:
                       resident_fails.append(resident)
                
                if not resident_succes:
                   raise Exception("No realizo ningún registro de la actividad porque los "
                                   " identificadores de los residentes no existen o no pertencen a la residencia "
                                   " de la sessión activa del usuario.")
                date_adjust = self._adjust_timezone(user, data['date'])
                
                register_ar = RecreationalActivity.create({
                            'date_execution':date_adjust,
                            'activity_type_id':nomen_activity_type.id,
                            'description': data['description'],
                            'user_id': user.id,
                        })

                if register_ar:
                    for resident in resident_succes:
                        RelResidentRecreationActivity.create({
                                'resident_id': resident.id,
                                'activity_id': register_ar.id,
                            })
                    answer = {
                                "id": register_ar.id,
                                "date": self._convert_to_iso(register_ar.date_execution),
                                "user_id": register_ar.user_id.id,
                                "user_name": register_ar.user_id.name,
                                "resident_associated": [ x.id for x in resident_succes ],
                                "resident_not_associated": [ x.id for x in resident_fails ],
                                "resident_not_found": resident_not_founds
                            }


            answer = {
                        "status": "success", 
                        "message": "Registro creado existosamente",  
                        "data": answer
                    }     
            _logger.info(f"Response: {answer}")
            return answer

        except Exception as e:
            return self._handle_error(e)  

    @http.route(
        "/api_serena/v1/list_activity_recreational_this_resident_range",
        type="json",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def list_activity_recreational_this_resident_range(self, **post):
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
                RecreationActivity = env["resident.recreation.activity.rel"].sudo()
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
                if not self._check_user_permissions(user, 'resident.recreation.activity.rel', self.CAN_READ, env):
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
                records = RecreationActivity.search_read(
                    domain=[
                        ("resident_id", "=", resident_id),
                        ("date_execution", ">=", date_start),
                        ("date_execution", "<=", date_end),
                    ],
                    fields=[
                        "id",
                        "date_execution",
                        "resident",
                        "user",
                        "description",
                        "activity_type",
                        "activity"
                    ],
                    order="date_execution DESC",
                )

                if records:
                    for wb in records:
                        answer.append(
                            {
                                "date_execution": self._convert_timezone(user,wb["date_execution"])
                                if wb["date_execution"]
                                else "",
                                "user": wb["user"],
                                "resident": wb["resident"],
                                "id": wb["id"],
                                "description": wb["description"], 
                                "activity_type": wb["activity_type"],
                                "activity": wb["activity"],
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
        "/api_serena/v1/list_activity_recreational_this_resident_all",
        type="json",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def list_activity_recreational_this_resident_all(self, **post):
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
                RecreationActivity = env["resident.recreation.activity.rel"].sudo()
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
                if not self._check_user_permissions(user, 'resident.recreation.activity.rel', self.CAN_READ, env):
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

                # Listar todas la notas de enfermería del residente
                answer = []
                records = RecreationActivity.search_read(
                    domain=[
                        ("resident_id", "=", resident_id),
                    ],
                    fields=[
                        "id",
                        "date_execution",
                        "resident",
                        "user",
                        "description",
                        "activity_type",
                        "activity"
                    ],
                    order="date_execution DESC",
                )

                if records:
                    for wb in records:
                        answer.append(
                            {
                                "date_execution": self._convert_timezone(user,wb["date_execution"])
                                if wb["date_execution"]
                                else "",
                                "user": wb["user"],
                                "resident": wb["resident"],
                                "id": wb["id"],
                                "description": wb["description"], 
                                "activity_type": wb["activity_type"],
                                "activity": wb["activity"],
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