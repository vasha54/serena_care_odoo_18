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

class NortonAssessmentController(BaseAPIController):

    def doc_register_norton_assessment(self):
        """
        Documentación Swagger para el método register_norton_assessment
        
        Returns:
            dict: Documentación Swagger para el endpoint de registrar evaluación Norton
        """
        return {
            "tags": ["Evaluación Geriatrica - Norton"],
            "summary": "Registrar evaluación de escala Norton a un residente",
            "description": """
            Endpoint para registrar una evaluación de escala Norton a un residente específico. 
            La escala Norton evalúa el riesgo de úlceras por presión con puntuaciones de 1-4 en cada categoría.
            Requiere autenticación JWT válida.

            **Cabeceras requeridas:**
            - Content-Type: application/json
            - Authorization: Bearer <token_jwt>

            **Puntuaciones de la escala Norton:**
            - Estado físico general: 1 (Muy malo) a 4 (Bueno)
            - Estado mental: 1 (Estupor) a 4 (Alerta)
            - Actividad: 1 (Encamado) a 4 (Deambula)
            - Movilidad: 1 (Inmóvil) a 4 (Completa)
            - Incontinencia: 1 (Doble) a 4 (Ninguna)
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
                                "description": "Identificador del residente al cual se le va registrar la evaluación Norton",
                                "example": 6
                            },
                            "date": {
                                "type": "string",
                                "format": "date-time",
                                "description": "Fecha y hora que se hace la evaluación en formato '%Y-%m-%d %H:%M:%S'",
                                "example": "2025-08-20 10:00:00"
                            },
                            "physical_condition": {
                                "type": "integer",
                                "description": "Estado físico general (1: Muy malo, 2: Malo, 3: Regular, 4: Bueno)",
                                "minimum": 1,
                                "maximum": 4,
                                "example": 3
                            },
                            "mental_state": {
                                "type": "integer",
                                "description": "Estado mental (1: Estupor, 2: Confuso, 3: Apático, 4: Alerta)",
                                "minimum": 1,
                                "maximum": 4,
                                "example": 4
                            },
                            "activity": {
                                "type": "integer",
                                "description": "Actividad (1: Encamado, 2: Sentado, 3: Ambula con ayuda, 4: Deambula)",
                                "minimum": 1,
                                "maximum": 4,
                                "example": 3
                            },
                            "mobility": {
                                "type": "integer",
                                "description": "Movilidad (1: Inmóvil, 2: Muy limitada, 3: Ligeramente limitada, 4: Completa)",
                                "minimum": 1,
                                "maximum": 4,
                                "example": 2
                            },
                            "incontinence": {
                                "type": "integer",
                                "description": "Incontinencia (1: Doble, 2: Incontinencia fecal, 3: Incontinencia urinaria, 4: Ninguna)",
                                "minimum": 1,
                                "maximum": 4,
                                "example": 3
                            }
                        },
                        "required": [
                            "resident_id",
                            "date",
                            "physical_condition",
                            "mental_state",
                            "activity",
                            "mobility",
                            "incontinence"
                        ]
                    }
                }
            ],
            "responses": {
                "200": {
                    "description": "Registro exitoso de evaluación Norton",
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
                                                "description": "Identificador del registro de la evaluación Norton",
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
                    "description": "Parámetros faltantes, inválidos o puntuaciones fuera de rango",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "example": "error"
                            },
                            "message": {
                                "type": "string",
                                "example": "Faltan parámetros requeridos o las puntuaciones deben estar entre 1 y 4"
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

    def doc_list_norton_assessment_this_resident_range(self):
        """
        Documentación Swagger para el método list_norton_assessment_this_resident_range
        
        Returns:
            dict: Documentación Swagger para el endpoint de listar evaluaciones Norton por rango de fechas
        """
        return {
            "tags": ["Evaluación Geriatrica - Norton"],
            "summary": "Listar las evaluaciones Norton de un residente en un rango de fechas",
            "description": """
            Endpoint para obtener todas las evaluaciones de escala Norton de un residente específico
            dentro de un rango de fechas determinado. Requiere autenticación JWT válida.

            **Cabeceras requeridas:**
            - Content-Type: application/json
            - Authorization: Bearer <token_jwt>

            **Interpretación de la puntuación total:**
            - 20 puntos: Sin riesgo
            - 15-19 puntos: Riesgo bajo
            - 12-14 puntos: Riesgo medio  
            - Menos de 12 puntos: Riesgo alto
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
                                "description": "Identificador del residente del cual se consultarán las evaluaciones Norton",
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
                    "description": "Lista de las evaluaciones Norton obtenida exitosamente",
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
                                                    "description": "Identificador del registro de la evaluación Norton",
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
                                                    "description": "Objeto con información del usuario que realizó la evaluación",
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
                                                "physical_condition": {
                                                    "type": "string",
                                                    "description": "Puntuación del estado físico general (1-4)",
                                                    "example": "3"
                                                },
                                                "mental_state": {
                                                    "type": "string",
                                                    "description": "Puntuación del estado mental (1-4)",
                                                    "example": "4"
                                                },
                                                "activity": {
                                                    "type": "string",
                                                    "description": "Puntuación de actividad (1-4)",
                                                    "example": "3"
                                                },
                                                "mobility": {
                                                    "type": "string",
                                                    "description": "Puntuación de movilidad (1-4)",
                                                    "example": "2"
                                                },
                                                "incontinence": {
                                                    "type": "string",
                                                    "description": "Puntuación de incontinencia (1-4)",
                                                    "example": "3"
                                                },
                                                "total_score": {
                                                    "type": "integer",
                                                    "description": "Puntuación total de la escala Norton (suma de todos los criterios)",
                                                    "example": 15
                                                },
                                                "risk_level": {
                                                    "type": "string",
                                                    "description": "Nivel de riesgo calculado basado en la puntuación total",
                                                    "example": "Riesgo bajo"
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

    def doc_list_norton_assessment_this_resident_all(self):
        """
        Documentación Swagger para el método list_norton_assessment_this_resident_all
        
        Returns:
            dict: Documentación Swagger para el endpoint de listar todas las evaluaciones Norton de un residente
        """
        return {
            "tags": ["Evaluación Geriatrica - Norton"],
            "summary": "Listar todas las evaluaciones Norton de un residente",
            "description": """
            Endpoint para obtener todos los registros de evaluaciones de escala Norton de un residente específico.
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
                                "description": "Identificador del residente del cual se consultarán todas las evaluaciones Norton",
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
                    "description": "Lista completa de las evaluaciones Norton obtenida exitosamente",
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
                                                    "description": "Identificador del registro de la evaluación Norton",
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
                                                    "description": "Objeto con información del usuario que realizó la evaluación",
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
                                                "physical_condition": {
                                                    "type": "string",
                                                    "description": "Puntuación del estado físico general (1-4)",
                                                    "example": "3"
                                                },
                                                "mental_state": {
                                                    "type": "string",
                                                    "description": "Puntuación del estado mental (1-4)",
                                                    "example": "4"
                                                },
                                                "activity": {
                                                    "type": "string",
                                                    "description": "Puntuación de actividad (1-4)",
                                                    "example": "3"
                                                },
                                                "mobility": {
                                                    "type": "string",
                                                    "description": "Puntuación de movilidad (1-4)",
                                                    "example": "2"
                                                },
                                                "incontinence": {
                                                    "type": "string",
                                                    "description": "Puntuación de incontinencia (1-4)",
                                                    "example": "3"
                                                },
                                                "total_score": {
                                                    "type": "integer",
                                                    "description": "Puntuación total de la escala Norton (suma de todos los criterios)",
                                                    "example": 15
                                                },
                                                "risk_level": {
                                                    "type": "string",
                                                    "description": "Nivel de riesgo calculado basado en la puntuación total",
                                                    "example": "Riesgo bajo"
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
        "/api_serena/v1/register_norton_assessment",
        type='json', 
        auth="none", 
        methods=['POST'], 
        csrf=False
    )
    def register_norton_assessment(self, **post):
        try:
            parameters = [
                'resident_id',
                'date',
                'physical_condition',
                'mental_state',
                'activity',
                'mobility',
                'incontinence',
            ]
            token = self._get_token()
            payload = self._get_payload(token)
            data = self._get_json_data(request.httprequest.data)
            self._check_existence_parameters(parameters, data)

            current_db = request.env.cr.dbname
            user_id = payload['user_id']
            residence_id = payload['residence_id']
            resident_id = data['resident_id']

            # Validar rango de valores (1-4)
            assessment_fields = [
                'physical_condition',
                'mental_state',
                'activity',
                'mobility',
                'incontinence'
            ]
            
            for field in assessment_fields:
                value = data[field]
                if not (1 <= value <= 4):
                    raise ValueError(f"El campo '{field}' debe tener un valor entre 1 y 4. Se recibió: {value}") 

            answer = {}
            # Usar Registry directamente como recomienda el warning
            registry = Registry(current_db)

            with registry.cursor() as cr:
                env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
                NortonAssessment = env['norton.assessment'].sudo()
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
                if not self._check_user_permissions(user, 'norton.assessment', self.CAN_CREATE, env):
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
                
                date_adjust = self._adjust_timezone(user, data['date'])

                # Registrar la evaluación de norton
                record_na = NortonAssessment.create({
                                'resident_id': resident.id,
                                'user_id':user.id,
                                'date': date_adjust, 
                                'physical_condition': str(data['physical_condition']),
                                'mental_state': str(data['mental_state']),
                                'activity': str(data['activity']),
                                'mobility': str(data['mobility']),
                                'incontinence': str(data['incontinence']),
                            })
                if record_na:
                    answer = {
                                "id": record_na.id,
                                "date": self._convert_to_iso(record_na.date),
                                "user_id": record_na.user_id.id,
                                "user_name": record_na.user_id.name,
                                "resident_id": record_na.resident_id.id,
                                "resident_name": record_na.resident_id.name,
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
        "/api_serena/v1/list_norton_assessment_this_resident_range",
        type="json",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def list_norton_assessment_this_resident_range(self, **post):
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
                NortonAssessment = env["norton.assessment"].sudo()
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
                if not self._check_user_permissions(user, 'norton.assessment', self.CAN_READ, env):
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

                # Listar todas las evaluaciones neurológicas del residente
                answer = []
                records = NortonAssessment.search_read(
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
                        "physical_condition",
                        "mental_state",
                        "activity",
                        "mobility",
                        "incontinence",
                        "total_score",
                        "risk_level",
                    ],
                    order="date DESC",
                )

                if records:
                    for na in records:
                        answer.append(
                            {
                                "date": self._convert_timezone(user,na["date"])
                                if na["date"]
                                else "",
                                "user": na["user"],
                                "resident": na["resident"],
                                "id": na["id"],
                                "physical_condition": na["physical_condition"],
                                "mental_state": na["mental_state"],
                                "activity": na["activity"],
                                "mobility": na["mobility"],
                                "incontinence": na["incontinence"],
                                "total_score": na["total_score"],
                                "risk_level": na["risk_level"],
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
        "/api_serena/v1/list_norton_assessment_this_resident_all",
        type="json",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def list_norton_assessment_this_resident_all(self, **post):
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
                NortonAssessment = env["norton.assessment"].sudo()
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
                if not self._check_user_permissions(user, 'norton.assessment', self.CAN_READ, env):
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

                # Listar todas las evaluaciones neurológicas del residente
                answer = []
                records = NortonAssessment.search_read(
                    domain=[
                        ("resident_id", "=", resident_id),
                    ],
                    fields=[
                        "id",
                        "date",
                        "resident",
                        "user",
                        "physical_condition",
                        "mental_state",
                        "activity",
                        "mobility",
                        "incontinence",
                        "total_score",
                        "risk_level",
                    ],
                    order="date DESC",
                )

                if records:
                    for na in records:
                        answer.append(
                            {
                                "date": self._convert_timezone(user, na["date"])
                                if na["date"]
                                else "",
                                "user": na["user"],
                                "resident": na["resident"],
                                "id": na["id"],
                                "physical_condition": na["physical_condition"],
                                "mental_state": na["mental_state"],
                                "activity": na["activity"],
                                "mobility": na["mobility"],
                                "incontinence": na["incontinence"],
                                "total_score": na["total_score"],
                                "risk_level": na["risk_level"],
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