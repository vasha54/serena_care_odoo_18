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


class MedicalIndicationController(BaseAPIController):
    def doc_list_medical_indication_this_resident(self):
        """
        Documentación Swagger para el método list_medical_indication_this_resident

        Returns:
            dict: Documentación Swagger para el endpoint de listado de indicaciones médicas
        """
        return {
            "tags": ["Indicaciones Médicas"],
            "summary": "Lista de indicaciones médicas de un residente",
            "description": """
            Retorna un listado de todas las indicaciones médicas de un residente específico. 
            Puede filtrarse por tipo de indicación (todas, generales o medicamentos).
            
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
                    "description": "Parámetros requeridos para la consulta",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "resident_id": {
                                "type": "integer",
                                "description": "Identificador entero del residente",
                                "example": 6,
                            },
                            "type_indication": {
                                "type": "string",
                                "description": "Tipo de indicación médica (all, general, medication)",
                                "enum": ["all", "general", "medication"],
                                "example": "all",
                            },
                        },
                        "required": ["resident_id", "type_indication"],
                    },
                },
            ],
            "security": [{"Bearer": []}],
            "responses": {
                "200": {
                    "description": "Listado de indicaciones médicas obtenido exitosamente",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "status": {
                                        "type": "string",
                                        "example": "success",
                                        "description": "Estado de la operación",
                                    },
                                    "message": {
                                        "type": "string",
                                        "example": "Datos obtenidos satifactoriamente",
                                        "description": "Mensaje descriptivo del resultado",
                                    },
                                    "data": {
                                        "type": "array",
                                        "description": "Lista de indicaciones médicas",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "id": {
                                                    "type": "string",
                                                    "description": "ID de la indicación con formato <tipo>_<id>",
                                                    "example": "medication_8",
                                                },
                                                "create_date": {
                                                    "type": "string",
                                                    "format": "date-time",
                                                    "description": "Fecha de creación de la indicación",
                                                    "example": "2025-08-19T03:13:01Z",
                                                },
                                                "resident_data": {
                                                    "type": "object",
                                                    "description": "Datos del residente",
                                                    "properties": {
                                                        "id": {
                                                            "type": "integer",
                                                            "example": 6,
                                                        },
                                                        "name": {
                                                            "type": "string",
                                                            "example": "Guadalupe Hernández Díaz",
                                                        },
                                                    },
                                                },
                                                "user_data": {
                                                    "type": "object",
                                                    "description": "Datos del usuario/doctor",
                                                    "properties": {
                                                        "id": {
                                                            "type": "integer",
                                                            "example": 2,
                                                        },
                                                        "name": {
                                                            "type": "string",
                                                            "example": "Administrator",
                                                        },
                                                    },
                                                },
                                                "note": {
                                                    "type": "string",
                                                    "description": "Texto de la indicación",
                                                    "example": "Medicamento: sdsd\nPresentación: JARABE\nVías de administración: Bucal",
                                                },
                                                "medicament_data": {
                                                    "type": "object",
                                                    "description": "Datos del medicamento (solo para tipo medication)",
                                                    "properties": {
                                                        "id": {
                                                            "type": "integer",
                                                            "example": 3,
                                                        },
                                                        "name": {
                                                            "type": "string",
                                                            "example": "sdsd",
                                                        },
                                                    },
                                                },
                                                "pharmaceutical_form": {
                                                    "type": "string",
                                                    "description": "Forma farmacéutica (solo para tipo medication)",
                                                    "example": "COMPRIMIDO",
                                                },
                                                "route_data": {
                                                    "type": "object",
                                                    "description": "Vía de administración (solo para tipo medication)",
                                                    "properties": {
                                                        "id": {
                                                            "type": "integer",
                                                            "example": 5,
                                                        },
                                                        "name": {
                                                            "type": "string",
                                                            "example": "Intratecal",
                                                        },
                                                    },
                                                },
                                                "dosage_amount": {
                                                    "type": "number",
                                                    "format": "float",
                                                    "description": "Cantidad de la dosis (solo para tipo medication)",
                                                    "example": 45.0,
                                                },
                                                "dosage_unit_data": {
                                                    "type": "object",
                                                    "description": "Unidad de medida de la dosis (solo para tipo medication)",
                                                    "properties": {
                                                        "id": {
                                                            "type": "integer",
                                                            "example": 136,
                                                        },
                                                        "name": {
                                                            "type": "string",
                                                            "example": "Libra",
                                                        },
                                                    },
                                                },
                                                "frequency_amount": {
                                                    "type": "integer",
                                                    "description": "Intervalo de tiempo entre suministros (solo para tipo medication)",
                                                    "example": 90,
                                                },
                                                "frequency_unit_data": {
                                                    "type": "object",
                                                    "description": "Unidad de medida de la frecuencia (solo para tipo medication)",
                                                    "properties": {
                                                        "id": {
                                                            "type": "integer",
                                                            "example": 115,
                                                        },
                                                        "name": {
                                                            "type": "string",
                                                            "example": "Minuto",
                                                        },
                                                    },
                                                },
                                                "start_date_medication": {
                                                    "type": "string",
                                                    "format": "date-time",
                                                    "description": "Fecha de inicio de medicación (solo para tipo medication)",
                                                    "example": "2025-08-25T15:00:00Z",
                                                },
                                                "end_date_medication": {
                                                    "type": "string",
                                                    "format": "date-time",
                                                    "description": "Fecha de fin de medicación (solo para tipo medication)",
                                                    "example": "2025-08-31T15:00:00Z",
                                                },
                                                "is_lifetime_medication": {
                                                    "type": "boolean",
                                                    "description": "Indica si es medicación de por vida (solo para tipo medication)",
                                                    "example": False,
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                            "examples": {
                                "all_indicaciones": {
                                    "summary": "Respuesta para tipo 'all'",
                                    "value": {
                                        "status": "success",
                                        "message": "Datos obtenidos satifactoriamente",
                                        "data": [
                                            {
                                                "id": "medication_8",
                                                "create_date": "2025-08-19T03:13:01Z",
                                                "resident_data": {
                                                    "id": 6,
                                                    "name": "Guadalupe Hernández Díaz",
                                                },
                                                "user_data": {
                                                    "id": 2,
                                                    "name": "Administrator",
                                                },
                                                "note": "Medicamento: sdsd\nPresentación: JARABE\nVías de administración: Bucal",
                                            },
                                            {
                                                "id": "general_2",
                                                "create_date": "2025-08-19T03:12:19Z",
                                                "resident_data": {
                                                    "id": 6,
                                                    "name": "Guadalupe Hernández Díaz",
                                                },
                                                "user_data": {
                                                    "id": 2,
                                                    "name": "Administrator",
                                                },
                                                "note": "Test wizard",
                                            },
                                        ],
                                    },
                                },
                                "medication_indicaciones": {
                                    "summary": "Respuesta para tipo 'medication'",
                                    "value": {
                                        "status": "success",
                                        "message": "Datos obtenidos satifactoriamente",
                                        "data": [
                                            {
                                                "id": 12,
                                                "create_date": "2025-08-23T15:43:08.006481Z",
                                                "resident_data": {
                                                    "id": 6,
                                                    "name": "Guadalupe Hernández Díaz",
                                                },
                                                "user_data": {
                                                    "id": 2,
                                                    "name": "Administrator",
                                                },
                                                "note": "Medicamento: sdsd\nForma farmacéutica: COMPRIMIDO\nVía de administración: Intratecal",
                                                "medicament_data": {
                                                    "id": 3,
                                                    "name": "sdsd",
                                                },
                                                "pharmaceutical_form": "COMPRIMIDO",
                                                "route_data": {
                                                    "id": 5,
                                                    "name": "Intratecal",
                                                },
                                                "dosage_amount": 45.0,
                                                "dosage_unit_data": {
                                                    "id": 136,
                                                    "name": "Libra",
                                                },
                                                "frequency_amount": 90,
                                                "frequency_unit_data": {
                                                    "id": 115,
                                                    "name": "Minuto",
                                                },
                                                "start_date_medication": "2025-08-25T15:00:00Z",
                                                "end_date_medication": "2025-08-31T15:00:00Z",
                                                "is_lifetime_medication": False,
                                            }
                                        ],
                                    },
                                },
                            },
                        }
                    },
                },
                "400": {
                    "description": "Parámetros inválidos en la solicitud",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "status": {"type": "string", "example": "error"},
                                    "message": {
                                        "type": "string",
                                        "example": "Parámetros inválidos",
                                    },
                                    "data": {"type": "null"},
                                    "pagination": {"type": "null"},
                                },
                            }
                        }
                    },
                },
                "401": {
                    "description": "Token inválido o no proporcionado",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "status": {"type": "string", "example": "error"},
                                    "message": {
                                        "type": "string",
                                        "example": "Token inválido o expirado",
                                    },
                                    "data": {"type": "null"},
                                    "pagination": {"type": "null"},
                                },
                            }
                        }
                    },
                },
                "403": {
                    "description": "Acceso denegado",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "status": {"type": "string", "example": "error"},
                                    "message": {
                                        "type": "string",
                                        "example": "Acceso denegado para este residente",
                                    },
                                    "data": {"type": "null"},
                                    "pagination": {"type": "null"},
                                },
                            }
                        }
                    },
                },
                "500": {
                    "description": "Error interno del servidor",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "status": {"type": "string", "example": "error"},
                                    "message": {
                                        "type": "string",
                                        "example": "Error interno del servidor",
                                    },
                                    "data": {"type": "null"},
                                    "pagination": {"type": "null"},
                                },
                            }
                        }
                    },
                },
            },
        }

    @http.route(
        "/api_serena/v1/list_medical_indication_this_resident",
        type="json",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def list_medical_indication_this_resident(self, **post):
        try:
            parameters = [
                "resident_id",
                "type_indication",
            ]
            token = self._get_token()
            payload = self._get_payload(token)
            data = self._get_json_data(request.httprequest.data)
            self._check_existence_parameters(parameters, data)

            current_db = request.env.cr.dbname
            user_id = payload["user_id"]
            residence_id = payload["residence_id"]
            resident_id = data["resident_id"]
            type_indication = data["type_indication"]

            type_vs_model_indication = {
                "all": "unified.medical.indication",
                "general": "medical.indication",
                "medication": "medical.medication",
            }

            model_indication = type_vs_model_indication.get(type_indication, None)

            if not model_indication:
                raise Exception(
                    "El tipo de indicación médica aún no está implementada "
                    "por el sistema actualmente"
                )

            answer = {}
            data = []
            # Usar Registry directamente como recomienda el warning
            registry = Registry(current_db)
            with registry.cursor() as cr:
                env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
                ModelIndication = env[model_indication].sudo()
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
                if not self._check_user_permissions(user, model_indication, self.CAN_READ, env):
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
                # Obtener las indicaciones médicas del residente ordenadas descendentemente
                # por la fecha de elaboración.
                list_fields = [
                    "id",
                    "create_date",
                    "resident_data",
                    "user_data",
                    "note",
                ]

                if model_indication == "medical.medication":
                    list_fields = list_fields + [
                        "medicament_data",
                        "pharmaceutical_form",
                        "route_data",
                        "dosage_amount",
                        "dosage_unit_data",
                        "frequency_amount",
                        "frequency_unit_data",
                        "start_date_medication",
                        "end_date_medication",
                        "is_lifetime_medication",
                    ]

                domain = [("resident_id", "=", resident_id)]

                if model_indication in ["medical.medication", "medical.indication"]:
                    domain.append(("active", "=", True))

                data = ModelIndication.search_read(
                    domain=domain,
                    fields=list_fields,
                    order="create_date desc",
                )
                fields_date = [
                    "create_date",
                    "start_date_medication",
                    "end_date_medication",
                ]
                for d in data:
                    for f in fields_date:
                        if d and f in d and d[f]:
                            d[f] = self._convert_to_iso(d[f])
            answer = {
                "status": "success",
                "message": "Datos obtenidos satifactoriamente",
                "data": data,
            }

            _logger.info(f"Response: {answer}")
            return answer
            # return Response(
            #     answer,
            #     headers={"Content-Type": "application/json"},
            # )
        except Exception as e:
            return self._handle_error(e)
