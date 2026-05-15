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


class MoodAssessmentAPIController(BaseAPIController):
    
    def doc_list_mood_assessment_this_resident_range(self):
        """
        Documentación Swagger para el método list_mood_assessment_this_resident_range

        Returns:
            dict: Documentación Swagger para el endpoint de listar evaluaciones de ánimo por rango de fechas
        """
        return {
            "tags": ["Evaluación de Ánimo"],
            "summary": "Listar evaluaciones de ánimo de un residente en un rango de fechas",
            "description": """
            Endpoint para obtener las evaluaciones de ánimo de un residente específico
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
                    "schema": {
                        "type": "object",
                        "properties": {
                            "resident_id": {
                                "type": "integer",
                                "description": "Identificador del residente del cual se consultarán las evaluaciones de ánimo",
                                "example": 4,
                            },
                            "date_start": {
                                "type": "string",
                                "format": "date",
                                "description": "Fecha de inicio del rango en formato YYYY-MM-DD",
                                "example": "2025-10-01",
                            },
                            "date_end": {
                                "type": "string",
                                "format": "date",
                                "description": "Fecha de fin del rango en formato YYYY-MM-DD",
                                "example": "2025-10-11",
                            },
                        },
                        "required": ["resident_id", "date_start", "date_end"],
                    },
                },
            ],
            "responses": {
                "200": {
                    "description": "Lista de evaluaciones de ánimo obtenida exitosamente",
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
                                    "result": {
                                        "type": "object",
                                        "properties": {
                                            "status": {
                                                "type": "string",
                                                "example": "success",
                                            },
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
                                                            "description": "Identificador del registro de evaluación de ánimo",
                                                            "example": 5,
                                                        },
                                                        "date": {
                                                            "type": "string",
                                                            "format": "date-time",
                                                            "description": "Fecha y hora del registro en formato YYYY-MM-DD HH:MM",
                                                            "example": "2025-10-11 14:38",
                                                        },
                                                        "user": {
                                                            "type": "object",
                                                            "description": "Objeto con información del usuario que realizó la evaluación",
                                                            "properties": {
                                                                "id": {
                                                                    "type": "integer",
                                                                    "description": "Identificador del usuario",
                                                                    "example": 10,
                                                                },
                                                                "name": {
                                                                    "type": "string",
                                                                    "description": "Nombre del usuario",
                                                                    "example": "Dr. Carlos Ruiz",
                                                                },
                                                            },
                                                        },
                                                        "resident": {
                                                            "type": "object",
                                                            "description": "Objeto con información del residente",
                                                            "properties": {
                                                                "id": {
                                                                    "type": "integer",
                                                                    "description": "Identificador del residente",
                                                                    "example": 4,
                                                                },
                                                                "name": {
                                                                    "type": "string",
                                                                    "description": "Nombre del residente",
                                                                    "example": "Ana Flores Ramírez",
                                                                },
                                                            },
                                                        },
                                                        "total_score": {
                                                            "type": "integer",
                                                            "description": "Puntaje total obtenido en la evaluación",
                                                            "example": 6,
                                                        },
                                                        "total_questions": {
                                                            "type": "integer",
                                                            "description": "Número total de preguntas en la evaluación",
                                                            "example": 15,
                                                        },
                                                        "mood_state_display": {
                                                            "type": "string",
                                                            "description": "Estado de ánimo interpretado basado en el puntaje",
                                                            "example": "Depresión leve",
                                                        },
                                                        "mood_state": {
                                                            "type": "object",
                                                            "description": "Objeto con información del estado de ánimo",
                                                            "properties": {
                                                                "id": {
                                                                    "type": "integer",
                                                                    "description": "Identificador del estado de ánimo",
                                                                    "example": 6,
                                                                },
                                                                "name": {
                                                                    "type": "string",
                                                                    "description": "Nombre del estado de ánimo",
                                                                    "example": "Enojado",
                                                                },
                                                                "order": {
                                                                    "type": "integer",
                                                                    "description": "Orden del estado de ánimo para visualización",
                                                                    "example": 3,
                                                                },
                                                                "image": {
                                                                    "type": "boolean",
                                                                    "description": "Indica si el estado de ánimo tiene una imagen asociada",
                                                                    "example": True,
                                                                },
                                                                "image_url": {
                                                                    "type": "string",
                                                                    "format": "uri",
                                                                    "description": "URL completa de la imagen del estado de ánimo (si existe)",
                                                                    "example": "http://localhost:8069/public/image/mood_state/6",
                                                                },
                                                            },
                                                        },
                                                    },
                                                },
                                            },
                                        },
                                    }
                                },
                            }
                        }
                    },
                },
                "400": {
                    "description": "Parámetros faltantes, inválidos o rango de fechas incorrecto",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "result": {
                                "type": "object",
                                "properties": {
                                    "status": {"type": "string", "example": "error"},
                                    "message": {
                                        "type": "string",
                                        "example": "Faltan parámetros requeridos o el rango de fecha es incorrecto",
                                    },
                                    "data": {"type": "null", "example": None},
                                },
                            }
                        },
                    },
                },
                "401": {
                    "description": "Token inválido o sesión no iniciada",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "result": {
                                "type": "object",
                                "properties": {
                                    "status": {"type": "string", "example": "error"},
                                    "message": {
                                        "type": "string",
                                        "example": "El usuario no tiene sessión iniciada",
                                    },
                                    "data": {"type": "null", "example": None},
                                },
                            }
                        },
                    },
                },
                "403": {
                    "description": "Acceso denegado - Residente no pertenece a la residencia del usuario",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "result": {
                                "type": "object",
                                "properties": {
                                    "status": {"type": "string", "example": "error"},
                                    "message": {
                                        "type": "string",
                                        "example": "El residente no se encuentra en la residencia en el que usuario se autentico",
                                    },
                                    "data": {"type": "null", "example": None},
                                },
                            }
                        },
                    },
                },
                "404": {
                    "description": "Residente no encontrado",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "result": {
                                "type": "object",
                                "properties": {
                                    "status": {"type": "string", "example": "error"},
                                    "message": {
                                        "type": "string",
                                        "example": "Residente no encontrado",
                                    },
                                    "data": {"type": "null", "example": None},
                                },
                            }
                        },
                    },
                },
                "500": {
                    "description": "Error interno del servidor",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "result": {
                                "type": "object",
                                "properties": {
                                    "status": {"type": "string", "example": "error"},
                                    "message": {
                                        "type": "string",
                                        "example": "Error interno del servidor",
                                    },
                                    "data": {"type": "null", "example": None},
                                },
                            }
                        },
                    },
                },
            },
            "security": [{"bearerAuth": []}],
        }

    def doc_list_mood_assessment_this_resident_all(self):
        """
        Documentación Swagger para el método list_mood_assessment_this_resident_all

        Returns:
            dict: Documentación Swagger para el endpoint de listar todas las evaluaciones de ánimo de un residente
        """
        return {
            "tags": ["Evaluación de Ánimo"],
            "summary": "Listar todas las evaluaciones de ánimo de un residente",
            "description": """
            Endpoint para obtener todos los registros de evaluaciones de ánimo de un residente específico.
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
                    "required": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "resident_id": {
                                "type": "integer",
                                "description": "Identificador del residente del cual se consultarán todas las evaluaciones de ánimo",
                                "example": 4,
                            }
                        },
                        "required": ["resident_id"],
                    },
                },
            ],
            "responses": {
                "200": {
                    "description": "Lista completa de evaluaciones de ánimo obtenida exitosamente",
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
                                    "result": {
                                        "type": "object",
                                        "properties": {
                                            "status": {
                                                "type": "string",
                                                "example": "success",
                                            },
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
                                                            "description": "Identificador del registro de evaluación de ánimo",
                                                            "example": 5,
                                                        },
                                                        "date": {
                                                            "type": "string",
                                                            "format": "date-time",
                                                            "description": "Fecha y hora del registro en formato YYYY-MM-DD HH:MM",
                                                            "example": "2025-10-11 14:38",
                                                        },
                                                        "user": {
                                                            "type": "object",
                                                            "description": "Objeto con información del usuario que realizó la evaluación",
                                                            "properties": {
                                                                "id": {
                                                                    "type": "integer",
                                                                    "description": "Identificador del usuario",
                                                                    "example": 10,
                                                                },
                                                                "name": {
                                                                    "type": "string",
                                                                    "description": "Nombre del usuario",
                                                                    "example": "Dr. Carlos Ruiz",
                                                                },
                                                            },
                                                        },
                                                        "resident": {
                                                            "type": "object",
                                                            "description": "Objeto con información del residente",
                                                            "properties": {
                                                                "id": {
                                                                    "type": "integer",
                                                                    "description": "Identificador del residente",
                                                                    "example": 4,
                                                                },
                                                                "name": {
                                                                    "type": "string",
                                                                    "description": "Nombre del residente",
                                                                    "example": "Ana Flores Ramírez",
                                                                },
                                                            },
                                                        },
                                                        "total_score": {
                                                            "type": "integer",
                                                            "description": "Puntaje total obtenido en la evaluación",
                                                            "example": 6,
                                                        },
                                                        "total_questions": {
                                                            "type": "integer",
                                                            "description": "Número total de preguntas en la evaluación",
                                                            "example": 15,
                                                        },
                                                        "mood_state_display": {
                                                            "type": "string",
                                                            "description": "Estado de ánimo interpretado basado en el puntaje",
                                                            "example": "Depresión leve",
                                                        },
                                                        "mood_state": {
                                                            "type": "object",
                                                            "description": "Objeto con información del estado de ánimo",
                                                            "properties": {
                                                                "id": {
                                                                    "type": "integer",
                                                                    "description": "Identificador del estado de ánimo",
                                                                    "example": 6,
                                                                },
                                                                "name": {
                                                                    "type": "string",
                                                                    "description": "Nombre del estado de ánimo",
                                                                    "example": "Enojado",
                                                                },
                                                                "order": {
                                                                    "type": "integer",
                                                                    "description": "Orden del estado de ánimo para visualización",
                                                                    "example": 3,
                                                                },
                                                                "image": {
                                                                    "type": "boolean",
                                                                    "description": "Indica si el estado de ánimo tiene una imagen asociada",
                                                                    "example": True,
                                                                },
                                                                "image_url": {
                                                                    "type": "string",
                                                                    "format": "uri",
                                                                    "description": "URL completa de la imagen del estado de ánimo (si existe)",
                                                                    "example": "http://localhost:8069/public/image/mood_state/6",
                                                                },
                                                            },
                                                        },
                                                    },
                                                },
                                            },
                                        },
                                    }
                                },
                            }
                        }
                    },
                },
                "400": {
                    "description": "Parámetros faltantes o inválidos",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "result": {
                                "type": "object",
                                "properties": {
                                    "status": {"type": "string", "example": "error"},
                                    "message": {
                                        "type": "string",
                                        "example": "Faltan parámetros requeridos",
                                    },
                                    "data": {"type": "null", "example": None},
                                },
                            }
                        },
                    },
                },
                "401": {
                    "description": "Token inválido o sesión no iniciada",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "result": {
                                "type": "object",
                                "properties": {
                                    "status": {"type": "string", "example": "error"},
                                    "message": {
                                        "type": "string",
                                        "example": "El usuario no tiene sessión iniciada",
                                    },
                                    "data": {"type": "null", "example": None},
                                },
                            }
                        },
                    },
                },
                "403": {
                    "description": "Acceso denegado - Residente no pertenece a la residencia del usuario",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "result": {
                                "type": "object",
                                "properties": {
                                    "status": {"type": "string", "example": "error"},
                                    "message": {
                                        "type": "string",
                                        "example": "El residente no se encuentra en la residencia en el que usuario se autentico",
                                    },
                                    "data": {"type": "null", "example": None},
                                },
                            }
                        },
                    },
                },
                "404": {
                    "description": "Residente no encontrado",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "result": {
                                "type": "object",
                                "properties": {
                                    "status": {"type": "string", "example": "error"},
                                    "message": {
                                        "type": "string",
                                        "example": "Residente no encontrado",
                                    },
                                    "data": {"type": "null", "example": None},
                                },
                            }
                        },
                    },
                },
                "500": {
                    "description": "Error interno del servidor",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "result": {
                                "type": "object",
                                "properties": {
                                    "status": {"type": "string", "example": "error"},
                                    "message": {
                                        "type": "string",
                                        "example": "Error interno del servidor",
                                    },
                                    "data": {"type": "null", "example": None},
                                },
                            }
                        },
                    },
                },
            },
            "security": [{"bearerAuth": []}],
        }

    @http.route(
        "/api_serena/v1/list_mood_assessment_this_resident_range",
        type="json",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def list_mood_assessment_this_resident_range(self, **post):
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
                MoodAssessment = env["mood.assessment"].sudo()
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
                if not self._check_user_permissions(user, 'mood.assessment', self.CAN_READ, env):
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

                answer = []
                records = MoodAssessment.search_read(
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
                        "mood_state",
                        "mood_state_display",
                    ],
                    order="create_date DESC",
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
                                "mood_state_display": wb["mood_state_display"],
                                "mood_state": wb["mood_state"],
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
        "/api_serena/v1/list_mood_assessment_this_resident_all",
        type="json",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def list_mood_assessment_this_resident_all(self, **post):
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
                MoodAssessment = env["mood.assessment"].sudo()
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
                if not self._check_user_permissions(user, 'mood.assessment', self.CAN_READ, env):
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

                answer = []
                records = MoodAssessment.search_read(
                    domain=[
                        ("resident_id", "=", resident_id),
                    ],
                    fields=[
                        "id",
                        "date",
                        "resident",
                        "user",
                        "mood_state",
                        "mood_state_display",
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
                                "mood_state_display": wb["mood_state_display"],
                                "mood_state": wb["mood_state"],
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
