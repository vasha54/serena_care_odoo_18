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

class VitalSignalController(BaseAPIController):

    def doc_register_vital_signs(self):
        """
        Documentación Swagger para el método register_vital_signs
        
        Returns:
            dict: Documentación Swagger para el endpoint de registrar signos vitales
        """
        return {
            "tags": ["Signos Vitales"],
            "summary": "Registrar signos vitales de un residente",
            "description": """
            Endpoint para registrar los signos vitales de un residente específico. Requiere autenticación JWT válida.

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
                                "description": "Identificador del residente al cual se le va tomar un registro de los signos vitales",
                                "example": 6
                            },
                            "temperature": {
                                "type": "number",
                                "format": "float",
                                "description": "Temperatura en grados Celsius (°C)",
                                "example": 36.6
                            },
                            "heart_rate": {
                                "type": "integer",
                                "description": "Ritmo cardíaco en pulsaciones por minuto (ppm)",
                                "example": 70
                            },
                            "systolic": {
                                "type": "integer",
                                "description": "Presión arterial sistólica en milímetros de mercurio (mmHg)",
                                "example": 118
                            },
                            "diastolic": {
                                "type": "integer",
                                "description": "Presión arterial diastólica en milímetros de mercurio (mmHg)",
                                "example": 77
                            },
                            "respiratory_rate": {
                                "type": "integer",
                                "description": "Frecuencia respiratoria en respiraciones por minuto (rpm)",
                                "example": 15
                            },
                            "weight": {
                                "type": "number",
                                "format": "float",
                                "description": "Peso corporal en kilogramos (Kg)",
                                "example": 64.9
                            },
                            "oxygen_saturation": {
                                "type": "integer",
                                "description": "Saturación de oxígeno en porcentaje (%)",
                                "example": 99
                            },
                            "glucose": {
                                "type": "number",
                                "format": "float",
                                "description": "Nivel de glucosa en miligramos por decilitro (mg/dL)",
                                "example": 88.0
                            },
                            "grip_strength": {
                                "type": "number",
                                "format": "float",
                                "description": "Fuerza de agarre en kilogramos (kg)",
                                "example": 26.5
                            },
                            "date": {
                                "type": "string",
                                "format": "date-time",
                                "description": "Fecha y hora que se hace la anotación en formato '%Y-%m-%d %H:%M:%S'",
                                "example": "2025-08-20 10:00:00"
                            },
                        },
                        "required": [
                            "resident_id",
                            "temperature",
                            "heart_rate",
                            "systolic",
                            "diastolic",
                            "respiratory_rate",
                            "weight",
                            "oxygen_saturation",
                            "glucose",
                            "grip_strength",
                            "date",
                        ]
                    }
                }
            ],
            "responses": {
                "200": {
                    "description": "Registro exitoso de signos vitales",
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
                                                "description": "Identificador del registro de signos vitales",
                                                "example": 28
                                            },
                                            "date": {
                                                "type": "string",
                                                "format": "date-time",
                                                "description": "Fecha y hora del registro en formato ISO",
                                                "example": "2025-08-17T21:15:44Z"
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

    def doc_list_vsigns_this_resident_range(self):
        """
        Documentación Swagger para el método list_vsigns_this_resident_range
        
        Returns:
            dict: Documentación Swagger para el endpoint de listar signos vitales por rango de fechas
        """
        return {
            "tags": ["Signos Vitales"],
            "summary": "Listar signos vitales de un residente en un rango de fechas",
            "description": """
            Endpoint para obtener todos los registros de signos vitales de un residente específico
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
                                "description": "Identificador del residente del cual se consultarán los signos vitales",
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
                                "example": "2025-08-17"
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
                    "description": "Lista de signos vitales obtenida exitosamente",
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
                                                    "description": "Identificador del registro de signos vitales",
                                                    "example": 28
                                                },
                                                "date": {
                                                    "type": "string",
                                                    "format": "date-time",
                                                    "description": "Fecha y hora del registro en formato YYYY-MM-DD HH:MM",
                                                    "example": "2025-08-17 21:15:44"
                                                },
                                                "user": {
                                                    "type": "object",
                                                    "description": "Objeto con información del usuario que realizó el registro",
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
                                                "temperature": {
                                                    "type": "number",
                                                    "format": "float",
                                                    "description": "Temperatura en grados Celsius (°C)",
                                                    "example": 36.6
                                                },
                                                "heart_rate": {
                                                    "type": "integer",
                                                    "description": "Ritmo cardíaco en pulsaciones por minuto (ppm)",
                                                    "example": 70
                                                },
                                                "systolic": {
                                                    "type": "integer",
                                                    "description": "Presión arterial sistólica en milímetros de mercurio (mmHg)",
                                                    "example": 118
                                                },
                                                "diastolic": {
                                                    "type": "integer",
                                                    "description": "Presión arterial diastólica en milímetros de mercurio (mmHg)",
                                                    "example": 77
                                                },
                                                "respiratory_rate": {
                                                    "type": "integer",
                                                    "description": "Frecuencia respiratoria en respiraciones por minuto (rpm)",
                                                    "example": 15
                                                },
                                                "weight": {
                                                    "type": "number",
                                                    "format": "float",
                                                    "description": "Peso corporal en kilogramos (Kg)",
                                                    "example": 64.9
                                                },
                                                "oxygen_saturation": {
                                                    "type": "integer",
                                                    "description": "Saturación de oxígeno en porcentaje (%)",
                                                    "example": 99
                                                },
                                                "glucose": {
                                                    "type": "number",
                                                    "format": "float",
                                                    "description": "Nivel de glucosa en miligramos por decilitro (mg/dL)",
                                                    "example": 88.0
                                                },
                                                "grip_strength": {
                                                    "type": "number",
                                                    "format": "float",
                                                    "description": "Fuerza de agarre en kilogramos (kg)",
                                                    "example": 26.5
                                                },
                                                "blood_pressure": {
                                                    "type": "string",
                                                    "description": "Presión arterial en formato sistólica/diastólica",
                                                    "example": "118/77"
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

    def doc_list_vsigns_this_resident_all(self):
        """
        Documentación Swagger para el método list_vsigns_this_resident_all
        
        Returns:
            dict: Documentación Swagger para el endpoint de listar todos los signos vitales de un residente
        """
        return {
            "tags": ["Signos Vitales"],
            "summary": "Listar todos los signos vitales de un residente",
            "description": """
            Endpoint para obtener todos los registros de signos vitales de un residente específico.
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
                                "description": "Identificador del residente del cual se consultarán todos los signos vitales",
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
                    "description": "Lista completa de signos vitales obtenida exitosamente",
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
                                                    "description": "Identificador del registro de signos vitales",
                                                    "example": 28
                                                },
                                                "date": {
                                                    "type": "string",
                                                    "format": "date-time",
                                                    "description": "Fecha y hora del registro en formato YYYY-MM-DD HH:MM",
                                                    "example": "2025-08-17 21:15:44"
                                                },
                                                "user": {
                                                    "type": "object",
                                                    "description": "Objeto con información del usuario que realizó el registro",
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
                                                "temperature": {
                                                    "type": "number",
                                                    "format": "float",
                                                    "description": "Temperatura en grados Celsius (°C)",
                                                    "example": 36.6
                                                },
                                                "heart_rate": {
                                                    "type": "integer",
                                                    "description": "Ritmo cardíaco en pulsaciones por minuto (ppm)",
                                                    "example": 70
                                                },
                                                "systolic": {
                                                    "type": "integer",
                                                    "description": "Presión arterial sistólica en milímetros de mercurio (mmHg)",
                                                    "example": 118
                                                },
                                                "diastolic": {
                                                    "type": "integer",
                                                    "description": "Presión arterial diastólica en milímetros de mercurio (mmHg)",
                                                    "example": 77
                                                },
                                                "respiratory_rate": {
                                                    "type": "integer",
                                                    "description": "Frecuencia respiratoria en respiraciones por minuto (rpm)",
                                                    "example": 15
                                                },
                                                "weight": {
                                                    "type": "number",
                                                    "format": "float",
                                                    "description": "Peso corporal en kilogramos (Kg)",
                                                    "example": 64.9
                                                },
                                                "oxygen_saturation": {
                                                    "type": "integer",
                                                    "description": "Saturación de oxígeno en porcentaje (%)",
                                                    "example": 99
                                                },
                                                "glucose": {
                                                    "type": "number",
                                                    "format": "float",
                                                    "description": "Nivel de glucosa en miligramos por decilitro (mg/dL)",
                                                    "example": 88.0
                                                },
                                                "grip_strength": {
                                                    "type": "number",
                                                    "format": "float",
                                                    "description": "Fuerza de agarre en kilogramos (kg)",
                                                    "example": 26.5
                                                },
                                                "blood_pressure": {
                                                    "type": "string",
                                                    "description": "Presión arterial en formato sistólica/diastólica",
                                                    "example": "118/77"
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
        "/api_serena/v1/register_vital_signs",
        type='json', 
        auth="none", 
        methods=['POST'], 
        csrf=False
    )
    def register_vital_signs(self, **post):
        try:
            parameters = [
                'resident_id',
                'temperature',
                'heart_rate',
                'systolic',
                'diastolic',
                'respiratory_rate',
                'weight',
                'oxygen_saturation',
                'glucose',
                'grip_strength',
                'date',
            ]
            token = self._get_token()
            payload = self._get_payload(token)
            data = self._get_json_data(request.httprequest.data)
            self._check_existence_parameters(parameters, data)
            
            current_db = request.env.cr.dbname
            user_id = payload['user_id']
            residence_id = payload['residence_id']
            resident_id = data['resident_id']

            answer = {}
            # Usar Registry directamente como recomienda el warning
            registry = Registry(current_db)

            with registry.cursor() as cr:
                env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
                VitalSigns = env['vital.signs'].sudo()
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
                if not self._check_user_permissions(user, 'vital.signs', self.CAN_CREATE, env):
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
                
                # Registrar la medición del signo vital
                record_vs = VitalSigns.create({
                                'resident_id': resident.id,
                                'user_id':user.id,
                                'temperature':data['temperature'],
                                'heart_rate':data['heart_rate'],
                                'systolic':data['systolic'],
                                'diastolic':data['diastolic'],
                                'respiratory_rate':data['respiratory_rate'],
                                'weight':data['weight'],
                                'oxygen_saturation':data['oxygen_saturation'],
                                'glucose':data['glucose'],
                                'grip_strength':data['grip_strength'],
                                'date': date_adjust, 
                            })
                if record_vs:
                    answer = {
                                "id": record_vs.id,
                                "date": self._convert_to_iso(record_vs.date),
                                "user_id": record_vs.user_id.id,
                                "user_name": record_vs.user_id.name,
                                "resident_id": record_vs.resident_id.id,
                                "resident_name": record_vs.resident_id.name,
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
        "/api_serena/v1/list_vsigns_this_resident_range",
        type="json",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def list_vsigns_this_resident_range(self, **post):
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
                VitalSigns = env["vital.signs"].sudo()
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
                if not self._check_user_permissions(user, 'vital.signs', self.CAN_READ, env):
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

                # Listar todas todos las tomas del signo vitales del residente
                answer = []
                records_wb = VitalSigns.search_read(
                    domain=[
                        ("resident_id", "=", resident_id),
                        ("date", ">=", date_start),
                        ("date", "<=", date_end),
                    ],
                    fields=[
                        "id",
                        "date",
                        "resident_data",
                        "user_data",
                        "temperature",
                        "heart_rate",
                        "systolic",
                        "diastolic",
                        "respiratory_rate",
                        "weight",
                        "oxygen_saturation",
                        "glucose",
                        "grip_strength",
                        "blood_pressure",
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
                                "user": wb["user_data"],
                                "resident": wb["resident_data"],
                                "id": wb["id"],
                                "temperature": wb["temperature"],
                                "heart_rate": wb["heart_rate"],
                                "systolic": wb["systolic"],
                                "diastolic": wb["diastolic"],
                                "respiratory_rate": wb["respiratory_rate"],
                                "weight": wb["weight"],
                                "oxygen_saturation": wb["oxygen_saturation"],
                                "glucose": wb["glucose"],
                                "grip_strength": wb["grip_strength"],
                                "blood_pressure": wb["blood_pressure"] 
                            }
                        )

            answer = {
                    "status": "success",
                    "message": "Datos obtenidos existosamente",
                    "data": answer,
                }
            _logger.info(f"Response: {answer}")
            return answer
        except Exception as e:
            return self._handle_error(e)

    @http.route(
        "/api_serena/v1/list_vsigns_this_resident_all",
        type="json",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def list_vsigns_this_resident_all(self, **post):
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
                VitalSigns = env["vital.signs"].sudo()
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
                if not self._check_user_permissions(user, 'vital.signs', self.CAN_READ, env):
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

                # Listar todas todos las tomas del signo vitales del residente
                answer = []
                records_wb = VitalSigns.search_read(
                    domain=[("resident_id", "=", resident_id)],
                    fields=[
                        "id",
                        "date",
                        "resident_data",
                        "user_data",
                        "temperature",
                        "heart_rate",
                        "systolic",
                        "diastolic",
                        "respiratory_rate",
                        "weight",
                        "oxygen_saturation",
                        "glucose",
                        "grip_strength",
                        "blood_pressure",
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
                                "user": wb["user_data"],
                                "resident": wb["resident_data"],
                                "id": wb["id"],
                                "temperature": wb["temperature"],
                                "heart_rate": wb["heart_rate"],
                                "systolic": wb["systolic"],
                                "diastolic": wb["diastolic"],
                                "respiratory_rate": wb["respiratory_rate"],
                                "weight": wb["weight"],
                                "oxygen_saturation": wb["oxygen_saturation"],
                                "glucose": wb["glucose"],
                                "grip_strength": wb["grip_strength"],
                                "blood_pressure": wb["blood_pressure"] 
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