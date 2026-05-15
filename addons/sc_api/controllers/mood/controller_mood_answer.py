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


class MoodAnswerAPIController(BaseAPIController):
    
    def doc_register_mood_answers(self):
        """
        Documentación Swagger para el método register_mood_answers

        Returns:
            dict: Documentación Swagger para el endpoint de registrar respuestas de ánimo
        """
        return {
            "tags": ["Evaluación de Ánimo"],
            "summary": "Registrar una evaluación de ánimo para un residente",
            "description": """
            Endpoint para registrar una nueva evaluación de ánimo (respuesta del cuestionario de ánimo)
            para un residente específico. Requiere autenticación JWT válida.

            **Cabeceras requeridas:**
            - Content-Type: application/json
            - Authorization: Bearer <token_jwt>

            **Notas importantes:**
            1. El estado de ánimo (mood_state_id) debe existir y estar activo en el sistema.
            2. El residente debe pertenecer a la misma residencia donde el usuario está autenticado.
            3. El usuario debe tener una sesión activa (token JWT válido).
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
                                "description": "Identificador del residente para el cual se registrará la evaluación de ánimo",
                                "example": 4,
                            },
                            "mood_state_id": {
                                "type": "integer",
                                "description": "Identificador del estado de ánimo seleccionado",
                                "example": 6,
                            },
                            "observations": {
                                "type": "string",
                                "description": "Observaciones clínicas adicionales sobre la evaluación",
                                "example": "El residente mostró signos de irritabilidad durante la evaluación",
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
                            "mood_state_id", 
                            "observations", 
                            "date"
                        ],
                    },
                },
            ],
            "responses": {
                "200": {
                    "description": "Evaluación de ánimo registrada exitosamente",
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
                                        "example": "Registro creado existosamente",
                                    },
                                    "data": {
                                        "type": "object",
                                        "properties": {
                                            "id": {
                                                "type": "integer",
                                                "description": "Identificador del registro de evaluación de ánimo creado",
                                                "example": 123,
                                            },
                                            "date": {
                                                "type": "string",
                                                "format": "date-time",
                                                "description": "Fecha y hora de creación del registro en formato ISO",
                                                "example": "2025-12-09T11:10:00",
                                            },
                                            "user_id": {
                                                "type": "integer",
                                                "description": "Identificador del usuario que realizó la evaluación",
                                                "example": 10,
                                            },
                                            "user_name": {
                                                "type": "string",
                                                "description": "Nombre del usuario que realizó la evaluación",
                                                "example": "Dr. Carlos Ruiz",
                                            },
                                            "resident_id": {
                                                "type": "integer",
                                                "description": "Identificador del residente evaluado",
                                                "example": 4,
                                            },
                                            "resident_name": {
                                                "type": "string",
                                                "description": "Nombre del residente evaluado",
                                                "example": "Ana Flores Ramírez",
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
                    "description": "Token inválido, expirado o sesión no iniciada",
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
                    "description": "Acceso denegado por alguna de las siguientes razones: "
                    "1. Residente no pertenece a la residencia del usuario\n"
                    "2. Usuario no tiene permisos para realizar la operación\n"
                    "3. Estado de ánimo no está activo",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "example": "error"},
                            "message": {
                                "type": "string",
                                "example": "El residente no se encuentra en la residencia en el que usuario se autenticó",
                            },
                            "data": {"type": "null", "example": None},
                        },
                    },
                },
                "404": {
                    "description": "Recurso no encontrado (residente o estado de ánimo)",
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
        "/api_serena/v1/register_mood_answers",
        type="json",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def register_mood_answers(self, **kwargs):
        try:
            parameters = [
                "resident_id",
                "mood_state_id",
                "observations",
                "date",
            ]
            token = self._get_token()
            payload = self._get_payload(token)
            data = self._get_json_data(request.httprequest.data)
            self._check_existence_parameters(parameters, data)

            current_db = request.env.cr.dbname
            user_id = payload["user_id"]
            residence_id = payload["residence_id"]
            resident_id = data["resident_id"]
            mood_state_id = data["mood_state_id"]
            observations_clinic = data["observations"]

            answer = {}
            # Usar Registry directamente como recomienda el warning
            registry = Registry(current_db)
            with registry.cursor() as cr:
                env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
                MoodState = env["mood.state"].sudo()
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
                if not self._check_user_permissions(user, 'mood.assessment', self.CAN_CREATE, env):
                    raise AccessDenied("El usuario no tiene los permisos para esta operación")

                # - Chequear que exista el residente
                resident = Resident.browse(resident_id)

                if not resident:
                    raise AccessDenied("Residente no encontrado")

                # - Chequear que en la residencia donde trabaja el usuario
                # en esta sessión sea la misma que la del residente
                if resident and resident.residence_id.id != residence_id:
                    raise AccessDenied(
                        "El residente no se encuentra en la residencia en el que\
 usuario se autentico"
                    )

                mood_state = MoodState.browse(mood_state_id)

                if not mood_state:
                    raise Exception(
                        f"No existe un estado de ánimo con id:'"
                        f"{mood_state_id}' registrado en el sistema"
                    )

                if not mood_state.active:
                    raise Exception(
                        f"El estado de ánimo '{mood_state.name}' "
                        f"no esta "
                        "activo en "
                        "el sistema"
                    )
                
                date_adjust = self._adjust_timezone(user, data['date'])
                # - Crear evaluacion
                assessment = MoodAssessment.create(
                    {
                        "resident_id": resident.id,
                        "user_id": user.id,
                        "date": date_adjust, 
                        "mood_state_id": int(mood_state_id),
                        "observations_clinic": observations_clinic,
                    }
                )

                if assessment:
                    answer = {
                        "id": assessment.id,
                        "date": self._convert_to_iso(assessment.date),
                        "user_id": assessment.user_id.id,
                        "user_name": assessment.user_id.name,
                        "resident_id": assessment.resident_id.id,
                        "resident_name": assessment.resident_id.name,
                    }

            answer = {
                "status": "success",
                "message": "Registro creado existosamente",
                "data": answer,
            }
            return answer
        except Exception as e:
            return self._handle_error(e)
