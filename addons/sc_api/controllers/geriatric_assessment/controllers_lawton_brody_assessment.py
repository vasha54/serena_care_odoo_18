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


class LawtonBrodyAssessmentAPIController(BaseAPIController):
    def doc_list_lawtonbrody_assessment_this_resident_range(self):
        """
        Documentación Swagger para el método list_lawtonbrody_assessment_this_resident_range

        Returns:
            dict: Documentación Swagger para el endpoint de listar evaluaciones de Lawton-Brody por rango de fechas
        """
        return {
            "tags": ["Evaluación Geriatrica - Lawton-Brody"],
            "summary": "Listar evaluaciones de Lawton-Brody de un residente en un rango de fechas",
            "description": """
            Endpoint para obtener las evaluaciones de Lawton-Brody de un residente específico
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
                                "description": "Identificador del residente del cual se consultarán las evaluaciones de Lawton-Brody",
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
                    "description": "Lista de evaluaciones de Lawton-Brody obtenida exitosamente",
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
                                                    "description": "Identificador del registro de evaluación de Lawton-Brody",
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
                                                "lawtonbrody_state_display": {
                                                    "type": "string",
                                                    "description": "Estado de Lawton-Brody interpretado basado en el puntaje",
                                                    "example": "Depresión leve",
                                                },
                                                "observations": {
                                                    "type": "string",
                                                    "description": "Nota de obervación sobre la ejecución de la evaluación",
                                                    "example": "El paciente no dudada mucho en contestar.",
                                                },
                                                "question_answers": {
                                                    "type": "array",
                                                    "description": "Lista de preguntas y respuestas de la evaluación",
                                                    "items": {
                                                        "type": "object",
                                                        "properties": {
                                                            "id": {
                                                                "type": "integer",
                                                                "description": "Identificador de la respuesta",
                                                                "example": 81,
                                                            },
                                                            "question_name": {
                                                                "type": "string",
                                                                "description": "Nombre de la pregunta",
                                                                "example": "Comer",
                                                            },
                                                            "choise_select_name": {
                                                                "type": "string",
                                                                "description": "Nombre de la opción seleccionada",
                                                                "example": "Ayuda parcial",
                                                            },
                                                            "choise_select_value": {
                                                                "type": "number",
                                                                "format": "float",
                                                                "description": "Valor de la opción seleccionada",
                                                                "example": 5.0,
                                                            },
                                                        },
                                                    },
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
                    "description": "Parámetros faltantes, inválidos o rango de fechas incorrecto",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "example": "error"},
                            "message": {
                                "type": "string",
                                "example": "Faltan parámetros requeridos o el rango de fecha es incorrecto",
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
                                "example": "El usuario no tiene sessión iniciada",
                            },
                            "data": {"type": "null", "example": None},
                        },
                    },
                },
                "403": {
                    "description": "Acceso denegado - Residente no pertenece a la residencia del usuario",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "example": "error"},
                            "message": {
                                "type": "string",
                                "example": "El residente no se encuentra en la residencia en el que usuario se autentico",
                            },
                            "data": {"type": "null", "example": None},
                        },
                    },
                },
                "404": {
                    "description": "Residente no encontrado",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "example": "error"},
                            "message": {
                                "type": "string",
                                "example": "Residente no encontrado",
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

    def doc_list_lawtonbrody_assessment_this_resident_all(self):
        """
        Documentación Swagger para el método list_lawtonbrody_assessment_this_resident_all

        Returns:
            dict: Documentación Swagger para el endpoint de listar todas las evaluaciones de Lawton-Brody de un residente
        """
        return {
            "tags": ["Evaluación Geriatrica - Lawton-Brody"],
            "summary": "Listar todas las evaluaciones de Lawton-Brody de un residente",
            "description": """
            Endpoint para obtener todos los registros de evaluaciones de Lawton-Brody de un residente específico.
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
                                "description": "Identificador del residente del cual se consultarán todas las evaluaciones de Lawton-Brody",
                                "example": 4,
                            }
                        },
                        "required": ["resident_id"],
                    },
                },
            ],
            "responses": {
                "200": {
                    "description": "Lista completa de evaluaciones de Lawton-Brody obtenida exitosamente",
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
                                                    "description": "Identificador del registro de evaluación de Lawton-Brody",
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
                                                "lawtonbrody_state_display": {
                                                    "type": "string",
                                                    "description": "Estado de Lawton-Brody interpretado basado en el puntaje",
                                                    "example": "Depresión leve",
                                                },
                                                "observations": {
                                                    "type": "string",
                                                    "description": "Nota de obervación sobre la ejecución de la evaluación",
                                                    "example": "El paciente no dudada mucho en contestar.",
                                                },
                                                "question_answers": {
                                                    "type": "array",
                                                    "description": "Lista de preguntas y respuestas de la evaluación",
                                                    "items": {
                                                        "type": "object",
                                                        "properties": {
                                                            "id": {
                                                                "type": "integer",
                                                                "description": "Identificador de la respuesta",
                                                                "example": 81,
                                                            },
                                                            "question_name": {
                                                                "type": "string",
                                                                "description": "Nombre de la pregunta",
                                                                "example": "Comer",
                                                            },
                                                            "choise_select_name": {
                                                                "type": "string",
                                                                "description": "Nombre de la opción seleccionada",
                                                                "example": "Ayuda parcial",
                                                            },
                                                            "choise_select_value": {
                                                                "type": "number",
                                                                "format": "float",
                                                                "description": "Valor de la opción seleccionada",
                                                                "example": 5.0,
                                                            },
                                                        },
                                                    },
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
                    "description": "Parámetros faltantes o inválidos",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "example": "error"},
                            "message": {
                                "type": "string",
                                "example": "Faltan parámetros requeridos",
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
                                "example": "El usuario no tiene sessión iniciada",
                            },
                            "data": {"type": "null", "example": None},
                        },
                    },
                },
                "403": {
                    "description": "Acceso denegado - Residente no pertenece a la residencia del usuario",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "example": "error"},
                            "message": {
                                "type": "string",
                                "example": "El residente no se encuentra en la residencia en el que usuario se autentico",
                            },
                            "data": {"type": "null", "example": None},
                        },
                    },
                },
                "404": {
                    "description": "Residente no encontrado",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "example": "error"},
                            "message": {
                                "type": "string",
                                "example": "Residente no encontrado",
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
        "/api_serena/v1/list_lawtonbrody_assessment_this_resident_range",
        type="json",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def list_lawtonbrody_assessment_this_resident_range(self, **post):
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
                LawtonBrodyAssessment = env["lawtonbrody.assessment"].sudo()
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

                if not self._check_user_permissions(user, 'lawtonbrody.assessment', self.CAN_READ, env):
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
                records = LawtonBrodyAssessment.search_read(
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
                        "total_score",
                        "total_questions",
                        "lawtonbrody_state_display",
                        "observations",
                        "question_answers_json",
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
                                "total_score": wb["total_score"],
                                "total_questions": wb["total_questions"],
                                "lawtonbrody_state_display": wb[
                                    "lawtonbrody_state_display"
                                ],
                                "observations": wb["observations"],
                                "question_answers": wb["question_answers_json"],
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
        "/api_serena/v1/list_lawtonbrody_assessment_this_resident_all",
        type="json",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def list_lawtonbrody_assessment_this_resident_all(self, **post):
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
                LawtonBrodyAssessment = env["lawtonbrody.assessment"].sudo()
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

                if not self._check_user_permissions(user, 'lawtonbrody.assessment', self.CAN_READ, env):
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
                records = LawtonBrodyAssessment.search_read(
                    domain=[
                        ("resident_id", "=", resident_id),
                    ],
                    fields=[
                        "id",
                        "date",
                        "resident",
                        "user",
                        "total_score",
                        "total_questions",
                        "lawtonbrody_state_display",
                        "observations",
                        "question_answers_json",
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
                                "total_score": wb["total_score"],
                                "total_questions": wb["total_questions"],
                                "lawtonbrody_state_display": wb[
                                    "lawtonbrody_state_display"
                                ],
                                "observations": wb["observations"],
                                "question_answers": wb["question_answers_json"],
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
