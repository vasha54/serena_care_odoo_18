import base64
import json
import jwt
import logging
import odoo

from odoo import _, http
from odoo.http import Response, request
from odoo.exceptions import AccessDenied
from odoo.modules.registry import Registry

from ..controllers_base import BaseAPIController

_logger = logging.getLogger(__name__)


class ResidentController(BaseAPIController):
    
    def doc_list_residents_this_residence(self):
        """
        Documentación Swagger para el método list_residents_this_residence

        Returns:
            dict: Documentación Swagger para el endpoint de listar residentes de una residencia
        """
        return {
            "tags": ["Residentes"],
            "summary": "Obtener los residentes de una residencia",
            "description": """
            Endpoint para obtener la lista de residentes de la residencia asociada al usuario autenticado.
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
                    "schema": {"type": "string"},
                    "example": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                },
                {
                    "name": "Content-Type",
                    "in": "header",
                    "required": True,
                    "description": "Tipo de contenido debe ser application/json",
                    "schema": {"type": "string", "enum": ["application/json"]},
                    "example": "application/json",
                },
                {
                    "name": "body",
                    "in": "body",
                    "required": False,
                    "description": "Este endpoint no requiere parámetros en el cuerpo, se puede enviar un objeto JSON vacío",
                    "schema": {"type": "object", "example": {}},
                },
            ],
            "responses": {
                "200": {
                    "description": "Lista de residentes obtenida exitosamente",
                    "headers": {
                        "Content-Type": {
                            "type": "string",
                            "description": "Tipo de contenido de la respuesta",
                        }
                    },
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "status": {"type": "string", "example": "success"},
                                    "message": {
                                        "type": "string",
                                        "example": "Datos obtenidos correctamente",
                                    },
                                    "data": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "id": {
                                                    "type": "integer",
                                                    "description": "Identificador numérico del residente en el sistema",
                                                    "example": 4,
                                                },
                                                "name": {
                                                    "type": "string",
                                                    "description": "Nombre completo del residente",
                                                    "example": "Ana Flores Ramírez",
                                                },
                                                "image_1920": {
                                                    "type": "boolean",
                                                    "description": "Verdadero si el residente posee una imagen y falso en caso contrario",
                                                    "example": False,
                                                },
                                                "image_1920_url": {
                                                    "type": "string",
                                                    "description": "Url de la imagen del residente o None si no tiene imagen",
                                                    "example": "http://<dominio.com>/web/image/public/resident/24/image_1920",
                                                },
                                            },
                                        },
                                    },
                                },
                            }
                        }
                    },
                },
                "400": {
                    "description": "Parámetros inválidos",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "example": "error"},
                            "message": {
                                "type": "string",
                                "example": "Encabezado de autorización inválido",
                            },
                            "data": {"type": "null", "example": None},
                        },
                    },
                },
                "401": {
                    "description": "Token inválido o sesión no iniciada",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "example": "error"},
                            "message": {
                                "type": "string",
                                "example": "Usuario no autenticado",
                            },
                            "data": {"type": "null", "example": None},
                        },
                    },
                },
                "403": {
                    "description": "Acceso denegado",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "example": "error"},
                            "message": {"type": "string", "example": "Access Denied"},
                            "data": {"type": "null", "example": None},
                        },
                    },
                },
                "500": {
                    "description": "Error interno del servidor",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "example": "error"},
                            "message": {
                                "type": "string",
                                "example": "Error interno del servidor",
                            },
                            "data": {"type": "null", "example": None},
                        },
                    },
                },
            },
            "security": [{"bearerAuth": []}],
        }

    def doc_list_familys_this_resident(self):
        """
        Documentación Swagger para el método list_familys_this_resident

        Returns:
            dict: Documentación Swagger para el endpoint de listar familiares de un residente
        """
        return {
            "tags": ["Residentes"],
            "summary": "Obtener los familiares de un residente específico",
            "description": """
            Endpoint para obtener la lista de familiares asociados a un residente específico.
            Requiere autenticación JWT válida y que el residente pertenezca a la residencia del usuario autenticado.

            **Cabeceras requeridas:**
            - Content-Type: application/json
            - Authorization: Bearer <token_jwt>

            **Parámetros requeridos en el cuerpo:**
            - resident_id: ID del residente para el cual se desean obtener los familiares
            """,
            "parameters": [
                {
                    "name": "Authorization",
                    "in": "header",
                    "required": True,
                    "description": "Token JWT de autenticación en formato 'Bearer {token}'",
                    "schema": {"type": "string"},
                    "example": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                },
                {
                    "name": "Content-Type",
                    "in": "header",
                    "required": True,
                    "description": "Tipo de contenido debe ser application/json",
                    "schema": {"type": "string", "enum": ["application/json"]},
                    "example": "application/json",
                },
                {
                    "name": "body",
                    "in": "body",
                    "required": True,
                    "description": "Parámetros requeridos para obtener los familiares del residente",
                    "schema": {
                        "type": "object",
                        "required": ["resident_id"],
                        "properties": {
                            "resident_id": {
                                "type": "integer",
                                "description": "ID del residente para el cual se desean obtener los familiares",
                                "example": 1,
                            }
                        },
                        "example": {"resident_id": 1},
                    },
                },
            ],
            "responses": {
                "200": {
                    "description": "Lista de familiares obtenida exitosamente",
                    "headers": {
                        "Content-Type": {
                            "type": "string",
                            "description": "Tipo de contenido de la respuesta",
                        }
                    },
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "status": {"type": "string", "example": "success"},
                                    "message": {
                                        "type": "string",
                                        "example": "Datos obtenidos existosamente",
                                    },
                                    "data": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "id": {
                                                    "type": "integer",
                                                    "description": "Identificador numérico de la relación familiar-residente",
                                                    "example": 4,
                                                },
                                                "is_contractor": {
                                                    "type": "boolean",
                                                    "description": "Indica si el familiar es el contratante",
                                                    "example": True,
                                                },
                                                "family_name": {
                                                    "type": "string",
                                                    "description": "Nombre completo del familiar",
                                                    "example": "Pedro Valido Marrero",
                                                },
                                                "family_ident": {
                                                    "type": "integer",
                                                    "description": "Identificador único del familiar",
                                                    "example": 1,
                                                },
                                                "family_phone": {
                                                    "type": "string",
                                                    "description": "Teléfono fijo del familiar",
                                                    "example": "452422401",
                                                },
                                                "family_mobile": {
                                                    "type": "string",
                                                    "description": "Teléfono móvil del familiar",
                                                    "example": "452422401",
                                                },
                                                "family_email": {
                                                    "type": "string",
                                                    "description": "Correo electrónico del familiar",
                                                    "example": "pedro.valido@gmail.com",
                                                },
                                                "family_address": {
                                                    "type": "string",
                                                    "description": "Dirección completa del familiar",
                                                    "example": "Calle Maceo54 Cidra",
                                                },
                                                "auth_level": {
                                                    "type": "array",
                                                    "description": "Lista de niveles de autorización del familiar",
                                                    "items": {
                                                        "type": "object",
                                                        "properties": {
                                                            "id": {
                                                                "type": "integer",
                                                                "description": "ID del nivel de autorización",
                                                                "example": 3,
                                                            },
                                                            "name": {
                                                                "type": "string",
                                                                "description": "Nombre del nivel de autorización",
                                                                "example": "Autorización para Salidas",
                                                            },
                                                        },
                                                    },
                                                },
                                                "kinship": {
                                                    "type": "object",
                                                    "description": "Información del parentesco del familiar con el residente",
                                                    "properties": {
                                                        "id": {
                                                            "type": "integer",
                                                            "description": "ID del tipo de parentesco",
                                                            "example": 15,
                                                        },
                                                        "name": {
                                                            "type": "string",
                                                            "description": "Nombre del tipo de parentesco",
                                                            "example": "bisabuela",
                                                        },
                                                    },
                                                },
                                                "family_image_1920": {
                                                    "type": "boolean",
                                                    "description": "Indica si el familiar tiene imagen de perfil",
                                                    "example": True,
                                                },
                                                "family_image_1920_url": {
                                                    "type": "string",
                                                    "description": "URL de la imagen del familiar o null si no tiene",
                                                    "example": "http://localhost:8069/public/image/family_resident/1",
                                                },
                                            },
                                        },
                                    },
                                },
                            }
                        }
                    },
                },
                "400": {
                    "description": "Parámetros inválidos o faltantes",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "example": "error"},
                            "message": {
                                "type": "string",
                                "example": "Parámetro resident_id es requerido",
                            },
                            "data": {"type": "null", "example": None},
                        },
                    },
                },
                "401": {
                    "description": "Token inválido o sesión no iniciada",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "example": "error"},
                            "message": {
                                "type": "string",
                                "example": "Usuario no autenticado",
                            },
                            "data": {"type": "null", "example": None},
                        },
                    },
                },
                "403": {
                    "description": "Acceso denegado - El residente no pertenece a la residencia del usuario",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "example": "error"},
                            "message": {
                                "type": "string",
                                "example": "El residente no se encuentra en la residencia en la que usuario se autenticó",
                            },
                            "data": {"type": "null", "example": None},
                        },
                    },
                },
                "500": {
                    "description": "Error interno del servidor",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "example": "error"},
                            "message": {
                                "type": "string",
                                "example": "Error interno del servidor",
                            },
                            "data": {"type": "null", "example": None},
                        },
                    },
                },
            },
            "security": [{"bearerAuth": []}],
        }

    def doc_get_info_basic_this_resident(self):
        """
        Documentación Swagger para el método get_info_basic_this_resident

        Returns:
            dict: Documentación Swagger para el endpoint de información básica de un residente
        """
        return {
            "tags": ["Residentes"],
            "summary": "Obtener información básica de un residente específico",
            "description": """
            Endpoint para obtener la información básica y detallada de un residente específico.
            Requiere autenticación JWT válida y que el residente pertenezca a la residencia del usuario autenticado.

            **Cabeceras requeridas:**
            - Content-Type: application/json
            - Authorization: Bearer <token_jwt>

            **Parámetros requeridos en el cuerpo:**
            - resident_id: ID del residente para el cual se desea obtener la información
            """,
            "parameters": [
                {
                    "name": "Authorization",
                    "in": "header",
                    "required": True,
                    "description": "Token JWT de autenticación en formato 'Bearer {token}'",
                    "schema": {"type": "string"},
                    "example": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                },
                {
                    "name": "Content-Type",
                    "in": "header",
                    "required": True,
                    "description": "Tipo de contenido debe ser application/json",
                    "schema": {"type": "string", "enum": ["application/json"]},
                    "example": "application/json",
                },
                {
                    "name": "body",
                    "in": "body",
                    "required": True,
                    "description": "Parámetros requeridos para obtener la información del residente",
                    "schema": {
                        "type": "object",
                        "required": ["resident_id"],
                        "properties": {
                            "resident_id": {
                                "type": "integer",
                                "description": "ID del residente para el cual se desea obtener la información básica",
                                "example": 4,
                            }
                        },
                        "example": {"resident_id": 4},
                    },
                },
            ],
            "responses": {
                "200": {
                    "description": "Información básica del residente obtenida exitosamente",
                    "headers": {
                        "Content-Type": {
                            "type": "string",
                            "description": "Tipo de contenido de la respuesta",
                        }
                    },
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "status": {"type": "string", "example": "success"},
                                    "message": {
                                        "type": "string",
                                        "example": "Datos obtenidos correctamente",
                                    },
                                    "data": {
                                        "type": "object",
                                        "properties": {
                                            "id": {
                                                "type": "integer",
                                                "description": "Identificador numérico del residente en el sistema",
                                                "example": 4,
                                            },
                                            "name": {
                                                "type": "string",
                                                "description": "Nombre completo del residente",
                                                "example": "Ana Flores Ramírez",
                                            },
                                            "active": {
                                                "type": "boolean",
                                                "description": "Estado de actividad del residente en el sistema",
                                                "example": True,
                                            },
                                            "birth_date": {
                                                "type": "string",
                                                "description": "Fecha de nacimiento del residente en formato ISO",
                                                "example": "1942-09-30Z",
                                            },
                                            "age": {
                                                "type": "integer",
                                                "description": "Edad del residente en años",
                                                "example": 83,
                                            },
                                            "dni": {
                                                "type": "string",
                                                "description": "Documento de identificación del residente",
                                                "example": "FORA420930JKL",
                                            },
                                            "sex": {
                                                "type": "object",
                                                "description": "Información del sexo del residente",
                                                "properties": {
                                                    "id": {
                                                        "type": "integer",
                                                        "description": "ID del sexo",
                                                        "example": 2,
                                                    },
                                                    "name": {
                                                        "type": "string",
                                                        "description": "Nombre del sexo",
                                                        "example": "Femenino",
                                                    },
                                                },
                                            },
                                            "weight": {
                                                "type": "number",
                                                "format": "float",
                                                "description": "Peso del residente en kg",
                                                "example": 61.7,
                                            },
                                            "residence": {
                                                "type": "object",
                                                "description": "Información de la residencia del residente",
                                                "properties": {
                                                    "id": {
                                                        "type": "integer",
                                                        "description": "ID de la residencia",
                                                        "example": 4,
                                                    },
                                                    "name": {
                                                        "type": "string",
                                                        "description": "Nombre de la residencia",
                                                        "example": "Casa Serena Monterrey",
                                                    },
                                                },
                                            },
                                            "phone": {
                                                "type": "string",
                                                "description": "Teléfono fijo del residente",
                                                "example": "+52 55 4567 8901",
                                            },
                                            "mobile": {
                                                "type": "string",
                                                "description": "Teléfono móvil del residente",
                                                "example": "+52 67 6789 9090",
                                            },
                                            "email": {
                                                "type": "string",
                                                "description": "Correo electrónico del residente",
                                                "example": "ana.flores@example.com",
                                            },
                                            "country": {
                                                "type": "object",
                                                "description": "País de residencia",
                                                "properties": {
                                                    "id": {
                                                        "type": "integer",
                                                        "description": "ID del país",
                                                        "example": 156,
                                                    },
                                                    "name": {
                                                        "type": "string",
                                                        "description": "Nombre del país",
                                                        "example": "Mexico",
                                                    },
                                                },
                                            },
                                            "province": {
                                                "type": "object",
                                                "description": "Provincia/estado de residencia",
                                                "properties": {
                                                    "id": {
                                                        "type": "integer",
                                                        "description": "ID de la provincia",
                                                        "example": 7,
                                                    },
                                                    "name": {
                                                        "type": "string",
                                                        "description": "Nombre de la provincia",
                                                        "example": "Chiapas",
                                                    },
                                                },
                                            },
                                            "municipality": {
                                                "type": "object",
                                                "description": "Municipio de residencia",
                                                "properties": {
                                                    "id": {
                                                        "type": "integer",
                                                        "description": "ID del municipio",
                                                        "example": 119,
                                                    },
                                                    "name": {
                                                        "type": "string",
                                                        "description": "Nombre del municipio",
                                                        "example": "Acacoyagua",
                                                    },
                                                },
                                            },
                                            "city": {
                                                "type": "string",
                                                "description": "Ciudad de residencia",
                                                "example": "Mexico",
                                            },
                                            "zip": {
                                                "type": "string",
                                                "description": "Código postal",
                                                "example": "4100",
                                            },
                                            "street": {
                                                "type": "string",
                                                "description": "Calle principal de la dirección",
                                                "example": "Maceo",
                                            },
                                            "street2": {
                                                "type": "string",
                                                "description": "Segunda línea de la dirección",
                                                "example": "Acana",
                                            },
                                            "street3": {
                                                "type": "string",
                                                "description": "Tercera línea de la dirección",
                                                "example": "LOpez Coma",
                                            },
                                            "street_number": {
                                                "type": "string",
                                                "description": "Número de la calle",
                                                "example": "54",
                                            },
                                            "diagnosis": {
                                                "type": "string",
                                                "description": "Diagnóstico médico del residente",
                                                "example": "Un texto",
                                            },
                                            "comment": {
                                                "type": "string",
                                                "description": "Comentarios adicionales sobre el residente (puede contener HTML)",
                                                "example": "<div data-oe-version=\"1.2\">Un texto</div>",
                                            },
                                            "observations": {
                                                "type": "string",
                                                "description": "Observaciones generales",
                                                "example": "Un texto",
                                            },
                                            "risk_falling": {
                                                "type": "string",
                                                "description": "Evaluación de riesgo de caídas",
                                                "example": "Un texto",
                                            },
                                            "risk_upp": {
                                                "type": "string",
                                                "description": "Evaluación de riesgo de úlceras por presión",
                                                "example": "Un texto",
                                            },
                                            "addictions": {
                                                "type": "array",
                                                "description": "Lista de adicciones del residente",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "id": {
                                                            "type": "integer",
                                                            "description": "ID de la adicción",
                                                            "example": 1,
                                                        },
                                                        "name": {
                                                            "type": "string",
                                                            "description": "Nombre de la adicción",
                                                            "example": "Alcohol",
                                                        },
                                                    },
                                                },
                                            },
                                            "allergys": {
                                                "type": "array",
                                                "description": "Lista de alergias del residente",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "id": {
                                                            "type": "integer",
                                                            "description": "ID de la alergia",
                                                            "example": 4,
                                                        },
                                                        "name": {
                                                            "type": "string",
                                                            "description": "Nombre de la alergia",
                                                            "example": "Naproxeno",
                                                        },
                                                    },
                                                },
                                            },
                                            "mother_family_history": {
                                                "type": "string",
                                                "description": "Historial familiar materno",
                                                "example": "Un texto",
                                            },
                                            "father_family_history": {
                                                "type": "string",
                                                "description": "Historial familiar paterno",
                                                "example": "Un texto",
                                            },
                                            "personal_pathological_history": {
                                                "type": "string",
                                                "description": "Historial patológico personal",
                                                "example": "Un texto",
                                            },
                                            "is_biomass_exposure": {
                                                "type": "boolean",
                                                "description": "Indica si el residente tiene exposición a biomasa",
                                                "example": False,
                                            },
                                            "is_smoking": {
                                                "type": "boolean",
                                                "description": "Indica si el residente fuma",
                                                "example": True,
                                            },
                                            "is_alcoholism": {
                                                "type": "boolean",
                                                "description": "Indica si el residente tiene alcoholismo",
                                                "example": True,
                                            },
                                            "p3_p2_ao_co": {
                                                "type": "string",
                                                "description": "Información médica específica P3/P2 AO/CO",
                                                "example": "Un texto",
                                            },
                                            "fur": {
                                                "type": "string",
                                                "description": "Fecha de última regla (solo para mujeres)",
                                                "example": "Un texto",
                                            },
                                            "immunizations": {
                                                "type": "string",
                                                "description": "Información sobre inmunizaciones/vacunas",
                                                "example": "Un texto",
                                            },
                                            "image_1920": {
                                                "type": "boolean",
                                                "description": "Indica si el residente tiene imagen de perfil",
                                                "example": True,
                                            },
                                            "image_1920_url": {
                                                "type": "string",
                                                "description": "URL de la imagen del residente o null si no tiene",
                                                "example": "http://localhost:8069/public/image/resident/4",
                                            },
                                        },
                                    },
                                },
                            }
                        }
                    },
                },
                "400": {
                    "description": "Parámetros inválidos o faltantes",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "example": "error"},
                            "message": {
                                "type": "string",
                                "example": "Parámetro resident_id es requerido",
                            },
                            "data": {"type": "null", "example": None},
                        },
                    },
                },
                "401": {
                    "description": "Token inválido o sesión no iniciada",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "example": "error"},
                            "message": {
                                "type": "string",
                                "example": "Usuario no autenticado",
                            },
                            "data": {"type": "null", "example": None},
                        },
                    },
                },
                "403": {
                    "description": "Acceso denegado - El residente no pertenece a la residencia del usuario",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "example": "error"},
                            "message": {
                                "type": "string",
                                "example": "El residente no se encuentra en la residencia en la que el usuario se autenticó",
                            },
                            "data": {"type": "null", "example": None},
                        },
                    },
                },
                "500": {
                    "description": "Error interno del servidor",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "example": "error"},
                            "message": {
                                "type": "string",
                                "example": "Error interno del servidor",
                            },
                            "data": {"type": "null", "example": None},
                        },
                    },
                },
            },
            "security": [{"bearerAuth": []}],
        }

    @http.route(
        "/api_serena/v1/list_residents_this_residence",
        type="json",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def list_residents_this_residence(self, **post):
        try:
            # Extraer token del encabezado Authorization
            auth_header = http.request.httprequest.headers.get("Authorization")
            if not auth_header or "Bearer " not in auth_header:
                raise Exception("Encabezado de autorización inválido")

            token = auth_header.split("Bearer ")[1].strip()

            # Obtener base de datos directamente del entorno actual
            current_db = request.env.cr.dbname

            answer = []
            # Usar Registry directamente como recomienda el warning
            registry = Registry(current_db)
            with registry.cursor() as cr:
                env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
                payload = jwt.decode(
                    token,
                    BaseAPIController.SECRET_KEY,
                    algorithms=[BaseAPIController.ALGORITHM],
                )
                user_id = payload["user_id"]
                residence_id = payload["residence_id"]

                # Buscar usuario en la base de datos actual
                users = (
                    env["res.users"]
                    .sudo()
                    .search([("id", "=", user_id), ("jwt_token", "=", token)])
                )

                if users:
                    # Obtener residentes usando el mismo entorno
                    data = (
                        env["resident"]
                        .sudo()
                        .search_read(
                            [("residence_id", "=", residence_id)],
                            ["id", "name", "image_1920"],
                        )
                    )
                    base_url = (
                        env["ir.config_parameter"].sudo().get_param("web.base.url")
                    )

                    for d in data:
                        if d.get("image_1920"):
                            d["image_1920"] = True
                            d[
                                "image_1920_url"
                            ] = f"{base_url}/public/image/resident/{d['id']}"
                        else:
                            d["image_1920"] = False
                            d["image_1920_url"] = None
                    answer = data
                else:
                    raise Exception("Usuario no autenticado")

            answer = {
                "status": "success",
                "message": "Datos obtenidos correctamente",
                "data": answer,
            }
            return answer
        except Exception as e:
            return self._handle_error(e)

    @http.route(
        "/api_serena/v1/list_familys_this_resident",
        type="json",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def list_familys_this_resident(self, **post):
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
                RelationshipResidentFamily = env["relationship.resident.family"].sudo()
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
                if not self._check_user_permissions(user, 'relationship.resident.family', self.CAN_READ, env):
                    raise AccessDenied("El usuario no tiene los permisos para esta operación")

                # - Chequear que exista el residente
                resident = Resident.browse(resident_id)

                if not resident:
                    raise AccessDenied("Residente no encontrado")

                # - Chequear que en la residencia donde trabaja el usuario
                # en esta sessión sea la misma que la del residente
                if resident and resident.residence_id.id != residence_id:
                    raise AccessDenied(
                        "El residente no se encuentra en la residencia en el que usuario se autentico"
                    )

                # Listar todas las mediciones del balance hídrico del residente
                answer = []
                records_rrf = RelationshipResidentFamily.search_read(
                    domain=[("resident_id", "=", resident_id)],
                    fields=[
                        "id",
                        "auth_level",
                        "kinship",
                        "is_contractor",
                        "family_ident",
                        "family_name",
                        "family_phone",
                        "family_mobile",
                        "family_email",
                        "family_image_1920",
                        "family_address",
                    ],
                )
                if records_rrf:
                    base_url = (
                        env["ir.config_parameter"].sudo().get_param("web.base.url")
                    )
                    for rrf in records_rrf:
                        record = {
                            "id": rrf["id"],
                            "is_contractor": rrf["is_contractor"],
                            "family_name": rrf["family_name"],
                            "family_ident": rrf["family_ident"],
                            "family_phone": rrf["family_phone"],
                            "family_mobile": rrf["family_mobile"],
                            "family_email": rrf["family_email"],
                            "family_address": rrf["family_address"],
                            "auth_level": rrf["auth_level"],
                            "kinship": rrf["kinship"],
                        }
                        if rrf["family_image_1920"]:
                            record["family_image_1920"] = True
                            record[
                                "family_image_1920_url"
                            ] = f"{base_url}/public/image/family_resident/{record['family_ident']}"
                        else:
                            record["family_image_1920"] = False
                            record["family_image_1920_url"] = None
                        answer.append(record)

            answer = {
                "status": "success",
                "message": "Datos obtenidos existosamente",
                "data": answer,
            }
            return answer
        except Exception as e:
            return self._handle_error(e)

    @http.route(
        "/api_serena/v1/info_basic_this_resident",
        type="json",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def get_info_basic_this_resident(self, **post):
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
                if not self._check_user_permissions(user, 'resident', self.CAN_READ, env):
                    raise AccessDenied("El usuario no tiene los permisos para esta operación")

                # - Chequear que exista el residente
                resident = Resident.browse(resident_id)

                if not resident:
                    raise AccessDenied("Residente no encontrado")

                # - Chequear que en la residencia donde trabaja el usuario
                # en esta sessión sea la misma que la del residente
                if resident and resident.residence_id.id != residence_id:
                    raise AccessDenied(
                        "El residente no se encuentra en la residencia en la que el usuario se autentico"
                    )

                base_url = env["ir.config_parameter"].sudo().get_param("web.base.url")

                data = {
                    "id": resident.id,
                    "name": resident.name,
                    "active": resident.active,
                    "birth_date": self._convert_to_iso(resident.birth_date),
                    "age": resident.age,
                    "dni": resident.dni,
                    "sex": resident.sex,
                    "weight": resident.weight,
                    "residence": resident.residence,
                    "phone": resident.phone,
                    "mobile": resident.mobile if resident.mobile else "",
                    "email": resident.email if resident.email else "",
                    "country": resident.country,
                    "province": resident.province,
                    "municipality": resident.municipality,
                    "city": resident.city if resident.city else "",
                    "zip": resident.zip if resident.zip else "",
                    "street": resident.street if resident.street else "",
                    "street2": resident.street2 if resident.street2 else "",
                    "street3": resident.street3 if resident.street3 else "",
                    "street_number": resident.street_number
                    if resident.street_number
                    else "",
                    "diagnosis": resident.diagnosis if resident.diagnosis else "",
                    "comment": resident.comment if resident.comment else "",
                    "observations": resident.observations
                    if resident.observations
                    else "",
                    "risk_falling": resident.risk_falling
                    if resident.risk_falling
                    else "",
                    "risk_upp": resident.risk_upp if resident.risk_upp else "",
                    "addictions": resident.addictions if resident.addictions else [],
                    "allergys": resident.allergys if resident.allergys else [],
                    "mother_family_history": resident.mother_family_history
                    if resident.mother_family_history
                    else "",
                    "father_family_history": resident.father_family_history
                    if resident.father_family_history
                    else "",
                    "personal_pathological_history": resident.personal_pathological_history,
                    "is_biomass_exposure": resident.is_biomass_exposure,
                    "is_smoking": resident.is_smoking,
                    "is_alcoholism": resident.is_alcoholism,
                    "p3_p2_ao_co": resident.p3_p2_ao_co if resident.p3_p2_ao_co else "",
                    "fur": resident.fur if resident.fur else "",
                    "immunizations": resident.immunizations
                    if resident.immunizations
                    else "",
                }

                if resident.image_1920:
                    data["image_1920"] = True
                    data[
                        "image_1920_url"
                    ] = f"{base_url}/public/image/resident/{resident.id}"
                else:
                    data["image_1920"] = False
                    data["image_1920_url"] = None
                answer = data

            answer = {
                "status": "success",
                "message": "Datos obtenidos correctamente",
                "data": answer,
            }
            return answer
        except Exception as e:
            return self._handle_error(e)
