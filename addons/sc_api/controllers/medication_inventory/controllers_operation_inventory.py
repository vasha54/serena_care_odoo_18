import base64
import json
from _ast import operator
from webbrowser import Opera

import jwt
import logging
import odoo

from odoo import _, http
from odoo.http import Response, request
from odoo.exceptions import AccessDenied
from odoo.modules.registry import Registry
from dateutil import parser
from datetime import datetime, time, timedelta

from ..controllers_base import BaseAPIController

_logger = logging.getLogger(__name__)


class OperationInventoryController(BaseAPIController):
    def doc_register_medication_intake(self):
        """
        Documentación Swagger para el método register_medication_intake

        Returns:
            dict: Documentación Swagger para el endpoint de registrar una operación
            salida de medicamento del inventario del residente.
        """
        return {
            "tags": ["Inventario de Medicamentos"],
            "summary": "Registrar consumo de medicamento del inventario",
            "description": """
            Endpoint para registrar la salida de medicamento del inventario de un residente cuando se le suministra una dosis

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
                                "description": "ID del residente al que se le suministra el medicamento",
                                "example": 123,
                            },
                            "dosage_uom_id": {
                                "type": "integer",
                                "description": "ID de la unidad de medida de la dosis suministrada",
                                "example": 5,
                            },
                            "medicament_id": {
                                "type": "integer",
                                "description": "ID del medicamento suministrado",
                                "example": 45,
                            },
                            "date": {
                                "type": "string",
                                "format": "date-time",
                                "description": "Fecha y hora que se hace la anotación en formato '%Y-%m-%d %H:%M:%S'",
                                "example": "2025-08-20 10:00:00",
                            },
                            "dosage_amount": {
                                "type": "number",
                                "format": "float",
                                "description": "Cantidad de medicamento suministrada",
                                "example": 2.5,
                            },
                            "indication_medication_id": {
                                "type": "integer",
                                "description": "ID de la indicación médica asociada a este suministro. Sino no tiene indicación médica asociada su valor puede ser -1 u omitir entre los parámetros",
                                "example": 5,
                            },
                        },
                        "required": [
                            "resident_id",
                            "dosage_uom_id",
                            "medicament_id",
                            "dosage_amount",
                            "date",
                        ],
                    },
                },
            ],
            "responses": {
                "200": {
                    "description": "Operación registrada exitosamente",
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
                                        "example": "Registro creado exitosamente",
                                    },
                                    "data": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "id": {
                                                    "type": "integer",
                                                    "description": "ID del registro de operación",
                                                    "example": 78,
                                                },
                                                "resident": {
                                                    "type": "object",
                                                    "description": "Objeto con información del residente que recibio el medicamento",
                                                    "properties": {
                                                        "id": {
                                                            "type": "integer",
                                                            "description": "Identificador del residente",
                                                            "example": 10,
                                                        },
                                                        "name": {
                                                            "type": "string",
                                                            "description": "Nombre del residenten",
                                                            "example": "Carlos Ruiz",
                                                        },
                                                    },
                                                },
                                                "uom": {
                                                    "type": "object",
                                                    "description": "Objeto con información de la unidad de medida utilizada en la medicación",
                                                    "properties": {
                                                        "id": {
                                                            "type": "integer",
                                                            "description": "Identificador de la unidad de medida",
                                                            "example": 1,
                                                        },
                                                        "name": {
                                                            "type": "string",
                                                            "description": "Nombre de la unidad de medida",
                                                            "example": "Kilogramo",
                                                        },
                                                    },
                                                },
                                                "medication": {
                                                    "type": "object",
                                                    "description": "Objeto con información del medicamento en la medicación",
                                                    "properties": {
                                                        "id": {
                                                            "type": "integer",
                                                            "description": "Identificador del medicamento",
                                                            "example": 1,
                                                        },
                                                        "name": {
                                                            "type": "string",
                                                            "description": "Nombre del medicamento",
                                                            "example": "Kilogramo",
                                                        },
                                                    },
                                                },
                                                "quantity": {
                                                    "type": "number",
                                                    "description": "Cantidad administrada",
                                                    "example": 2.5,
                                                },
                                                "reason": {
                                                    "type": "string",
                                                    "description": "Razón de la administración",
                                                    "example": "Dosis diaria prescrita",
                                                },
                                                "date": {
                                                    "type": "string",
                                                    "format": "YYYY-MM-DD HH:MM",
                                                    "description": "Fecha y hora de la administración",
                                                    "example": "2024-01-15 10:30",
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
                    "description": "Error en los parámetros de entrada",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "example": "error"},
                            "message": {
                                "type": "string",
                                "example": "Parámetros requeridos no encontrados",
                            },
                        },
                    },
                },
                "401": {
                    "description": "Error de autenticación o permisos",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "example": "error"},
                            "message": {
                                "type": "string",
                                "example": "Usuario no encontrado",
                            },
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
                        },
                    },
                },
            },
        }

    def doc_all_medicated_this_residents_last24h(self):
        """
        Documentación Swagger para el método get_all_medicated_this_residents_last24h

        Returns:
            dict: Documentación Swagger para el endpoint de obtener medicaciones
            de un residente específico en las últimas 24 horas.
        """
        return {
            "tags": ["Inventario de Medicamentos"],
            "summary": "Obtener medicaciones de un residente en las últimas 24h",
            "description": """
            Endpoint para obtener todas las medicaciones administradas a un residente específico
            en las últimas 24 horas desde una fecha de referencia.
    
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
                            "date": {
                                "type": "string",
                                "format": "date-time",
                                "description": "Fecha de referencia para "
                                "calcular las últimas 24 "
                                "horas. Formato YYYY-MM-DD "
                                "HH:MM",
                                "example": "2024-01-15 14:30",
                            },
                            "resident_id": {
                                "type": "integer",
                                "description": "ID del residente para filtrar las medicaciones",
                                "example": 123,
                            },
                        },
                        "required": ["date", "resident_id"],
                    },
                },
            ],
            "responses": {
                "200": {
                    "description": "Datos obtenidos exitosamente",
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
                                        "example": "Datos obtenidos exitosamente",
                                    },
                                    "data": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "id": {
                                                    "type": "integer",
                                                    "description": "ID del registro de operación",
                                                    "example": 78,
                                                },
                                                "resident": {
                                                    "type": "object",
                                                    "description": "Objeto con información del residente que recibio el medicamento",
                                                    "properties": {
                                                        "id": {
                                                            "type": "integer",
                                                            "description": "Identificador del residente",
                                                            "example": 10,
                                                        },
                                                        "name": {
                                                            "type": "string",
                                                            "description": "Nombre del residenten",
                                                            "example": "Carlos Ruiz",
                                                        },
                                                    },
                                                },
                                                "uom": {
                                                    "type": "object",
                                                    "description": "Objeto con información de la unidad de medida utilizada en la medicación",
                                                    "properties": {
                                                        "id": {
                                                            "type": "integer",
                                                            "description": "Identificador de la unidad de medida",
                                                            "example": 1,
                                                        },
                                                        "name": {
                                                            "type": "string",
                                                            "description": "Nombre de la unidad de medida",
                                                            "example": "Kilogramo",
                                                        },
                                                    },
                                                },
                                                "medication": {
                                                    "type": "object",
                                                    "description": "Objeto con información del medicamento en la medicación",
                                                    "properties": {
                                                        "id": {
                                                            "type": "integer",
                                                            "description": "Identificador del medicamento",
                                                            "example": 1,
                                                        },
                                                        "name": {
                                                            "type": "string",
                                                            "description": "Nombre del medicamento",
                                                            "example": "Kilogramo",
                                                        },
                                                    },
                                                },
                                                "quantity": {
                                                    "type": "number",
                                                    "description": "Cantidad administrada",
                                                    "example": 2.5,
                                                },
                                                "reason": {
                                                    "type": "string",
                                                    "description": "Razón de la administración",
                                                    "example": "Dosis diaria prescrita",
                                                },
                                                "date": {
                                                    "type": "string",
                                                    "format": "YYYY-MM-DD HH:MM",
                                                    "description": "Fecha y hora de la administración",
                                                    "example": "2024-01-15 10:30",
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
                    "description": "Error en los parámetros de entrada",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "example": "error"},
                            "message": {
                                "type": "string",
                                "example": "Parámetros requeridos no encontrados",
                            },
                        },
                    },
                },
                "401": {
                    "description": "Error de autenticación o permisos",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "example": "error"},
                            "message": {
                                "type": "string",
                                "example": "Usuario no encontrado",
                            },
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
                        },
                    },
                },
            },
        }

    def doc_all_medicated_residents_this_residence_last24h(self):
        """
        Documentación Swagger para el método get_all_medicated_residents_this_residence_last24h

        Returns:
            dict: Documentación Swagger para el endpoint de obtener todas las medicaciones
            de todos los residentes de una residencia en las últimas 24 horas.
        """
        return {
            "tags": ["Inventario de Medicamentos"],
            "summary": "Obtener medicaciones de todos los residentes de una residencia en las últimas 24h",
            "description": """
            Endpoint para obtener todas las medicaciones administradas a todos los residentes
            de una residencia en las últimas 24 horas desde una fecha de referencia.
    
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
                            "date": {
                                "type": "string",
                                "format": "date-time",
                                "description": "Fecha de referencia para calcular las últimas 24 horas formato YYYY-MM-DD HH:MM",
                                "example": "2024-01-15 10:30",
                            }
                        },
                        "required": ["date"],
                    },
                },
            ],
            "responses": {
                "200": {
                    "description": "Datos obtenidos exitosamente",
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
                                        "example": "Datos obtenidos exitosamente",
                                    },
                                    "data": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "id": {
                                                    "type": "integer",
                                                    "description": "ID del registro de operación",
                                                    "example": 78,
                                                },
                                                "resident": {
                                                    "type": "object",
                                                    "description": "Información del residente asociado a la medicación",
                                                    "properties": {
                                                        "id": {
                                                            "type": "integer",
                                                            "description": "Identificador del residente",
                                                            "example": 4,
                                                        },
                                                        "name": {
                                                            "type": "string",
                                                            "description": "Nombre completo del residente",
                                                            "example": "Ana Flores Ramírez",
                                                        },
                                                    },
                                                },
                                                "user": {
                                                    "type": "object",
                                                    "description": "Información del usuario que realizo la medicación",
                                                    "properties": {
                                                        "id": {
                                                            "type": "integer",
                                                            "description": "Identificador del usuario",
                                                            "example": 2,
                                                        },
                                                        "name": {
                                                            "type": "string",
                                                            "description": "Nombre del usuario",
                                                            "example": "Administrator",
                                                        },
                                                    },
                                                },
                                                "uom": {
                                                    "type": "object",
                                                    "description": "Información de la unidad de medida",
                                                    "properties": {
                                                        "id": {
                                                            "type": "integer",
                                                            "description": "Identificador de la unidad de medida",
                                                            "example": 2,
                                                        },
                                                        "name": {
                                                            "type": "string",
                                                            "description": "Nombre de la unidad de medida",
                                                            "example": "Kilogramo",
                                                        },
                                                    },
                                                },
                                                "medication": {
                                                    "type": "object",
                                                    "description": "Información del  medicamento suministrado",
                                                    "properties": {
                                                        "id": {
                                                            "type": "integer",
                                                            "description": "Identificador del medicamento suministrado",
                                                            "example": 2,
                                                        },
                                                        "name": {
                                                            "type": "string",
                                                            "description": "Nombre del medicamento suministrado",
                                                            "example": "Aspirina",
                                                        },
                                                    },
                                                },
                                                "quantity": {
                                                    "type": "number",
                                                    "description": "Cantidad administrada",
                                                    "example": 2.5,
                                                },
                                                "reason": {
                                                    "type": "string",
                                                    "description": "Razón de la administración",
                                                    "example": "Dosis diaria prescrita",
                                                },
                                                "pharmaceutical_form": {
                                                    "type": "string",
                                                    "description": "Forma de presentación o farmaceutica del medicamento",
                                                    "example": "Capsula",
                                                },
                                                "date": {
                                                    "type": "string",
                                                    "format": "date-time",
                                                    "description": "Fecha y hora de la administración",
                                                    "example": "2024-01-15 10:30",
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
                    "description": "Error en los parámetros de entrada",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "example": "error"},
                            "message": {
                                "type": "string",
                                "example": "Parámetros requeridos no encontrados",
                            },
                        },
                    },
                },
                "401": {
                    "description": "Error de autenticación o permisos",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "example": "error"},
                            "message": {
                                "type": "string",
                                "example": "Usuario no encontrado",
                            },
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
                        },
                    },
                },
            },
        }

    @http.route(
        "/api_serena/v1/all_medicated_this_residents_last24h",
        type="json",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def get_all_medicated_this_residents_last24h(self, **post):
        try:
            parameters = [
                "date",
                "resident_id",
            ]
            token = self._get_token()
            payload = self._get_payload(token)
            data = self._get_json_data(request.httprequest.data)
            self._check_existence_parameters(parameters, data)

            current_db = request.env.cr.dbname
            residence_id = payload["residence_id"]
            user_id = payload["user_id"]
            resident_id = data["resident_id"]

            answer = []
            # Usar Registry directamente como recomienda el warning
            registry = Registry(current_db)

            with registry.cursor() as cr:
                env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
                OperationInventory = env["operation.inventory"].sudo()
                Resident = env["resident"].sudo()
                ResUsers = env["res.users"].sudo()
                resident = None
                user = None
                # - Chequear que usuario tenga sessión activa
                user = ResUsers.browse(user_id)

                if not user:
                    raise AccessDenied("Usuario no encontrado")

                if not user.jwt_token or not user.token_expiration:
                    raise AccessDenied("El usuario no tiene sessión iniciada")

                # - Chequar que el usuario tenga los permisos para hacer
                if not self._check_user_permissions(user, 'operation.inventory', self.CAN_READ, env):
                    raise AccessDenied(
                        "El usuario no tiene los permisos para esta operación")

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

                if resident:
                    date_str = data["date"]
                    date_str = self._adjust_timezone(user, date_str)
                    date_end = parser.parse(date_str)
                    date_start = date_end - timedelta(hours=24)

                    operations = OperationInventory.search_read(
                        domain=[
                            ("resident_id", "=", resident.id),
                            ("operation_type", "=", "out"),
                            ("date", ">=", date_start),
                            ("date", "<=", date_end),
                        ],
                        fields=[
                            "id",
                            "resident",
                            "uom",
                            "medication",
                            "quantity",
                            "reason",
                            "date",
                        ],
                        order="date DESC",
                    )
                    if operations:
                        for operation in operations:
                            operation["date"] = operation.pop("date", False)
                            operation["date"] = self._convert_timezone(
                                user, operation["date"]
                            )
                            answer.append(operation)
            answer = {
                "status": "success",
                "message": "Datos obtenidos existosamente",
                "data": answer,
            }
            return answer
        except Exception as e:
            return self._handle_error(e)

    @http.route(
        "/api_serena/v1/all_medicated_residents_this_residence_last24h",
        type="json",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def get_all_medicated_residents_this_residence_last24h(self, **post):
        try:
            parameters = [
                "date",
            ]
            token = self._get_token()
            payload = self._get_payload(token)
            data = self._get_json_data(request.httprequest.data)
            self._check_existence_parameters(parameters, data)

            current_db = request.env.cr.dbname
            residence_id = payload["residence_id"]
            user_id = payload["user_id"]

            answer = []
            # Usar Registry directamente como recomienda el warning
            registry = Registry(current_db)

            with registry.cursor() as cr:
                env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
                OperationInventory = env["operation.inventory"].sudo()
                Resident = env["resident"].sudo()
                residents = Resident.search_read(
                    domain=[("residence_id", "=", int(residence_id))],
                    fields=["id", "name"],
                )
                ResUsers = env["res.users"].sudo()
                user = None
                # - Chequear que usuario tenga sessión activa
                user = ResUsers.browse(user_id)

                if not user:
                    raise AccessDenied("Usuario no encontrado")

                if not user.jwt_token or not user.token_expiration:
                    raise AccessDenied("El usuario no tiene sessión iniciada")

                # - Chequar que el usuario tenga los permisos para hacer
                if not self._check_user_permissions(user, 'operation.inventory', self.CAN_READ, env):
                    raise AccessDenied(
                        "El usuario no tiene los permisos para esta operación")

                date_str = data["date"]
                date_str = self._adjust_timezone(user, date_str)
                date_end = parser.parse(date_str)
                date_start = date_end - timedelta(hours=24)

                if residents:
                    ids = [d["id"] for d in residents]

                    operations = OperationInventory.search_read(
                        domain=[
                            ("resident_id", "in", ids),
                            ("operation_type", "=", "out"),
                            ("date", ">=", date_start),
                            ("date", "<=", date_end),
                        ],
                        fields=[
                            "id",
                            "resident",
                            "user",
                            "uom",
                            "medication",
                            "pharmaceutical_form",
                            "quantity",
                            "reason",
                            "date",
                        ],
                        order="date DESC",
                    )
                    if operations:
                        for operation in operations:
                            operation["date"] = operation.pop("date", False)
                            operation["date"] = self._convert_timezone(
                                user, operation["date"]
                            )
                            answer.append(operation)
            answer = {
                "status": "success",
                "message": "Datos obtenidos existosamente",
                "data": answer,
            }
            return answer
        except Exception as e:
            return self._handle_error(e)

    @http.route(
        "/api_serena/v1/register_medication_intake",
        type="json",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def register_medication_intake(self, **post):
        try:
            parameters = [
                "resident_id",
                "dosage_uom_id",
                "medicament_id",
                "dosage_amount",
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
            uom_id = data["dosage_uom_id"]
            medicament_id = data["medicament_id"]
            indication_medication_id = (
                data["indication_medication_id"]
                if "indication_medication_id" in data
                else False
            )
            dosage_amount = data["dosage_amount"]

            answer = {}
            # Usar Registry directamente como recomienda el warning
            registry = Registry(current_db)

            with registry.cursor() as cr:
                env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
                OperationInventory = env["operation.inventory"].sudo()
                MedicationInventory = env["medication.inventory"].sudo()
                MedicamentProduct = env["medicament.product"].sudo()
                UoM = env["uom.uom"].sudo()
                CatOuM = env["uom.category"].sudo()
                MedicalMedication = env["medical.medication"].sudo()
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
                if not self._check_user_permissions(user, 'operation.inventory', self.CAN_CREATE, env):
                    raise AccessDenied(
                        "El usuario no tiene los permisos para esta operación")

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

                uom = UoM.browse(uom_id)
                if not uom:
                    raise Exception(
                        "La unidad de medida de la dosis de medicamento suministrada al residente no existe en el sistema"
                    )

                cat_uom = CatOuM.browse(uom.category_id.id)

                medicament = MedicamentProduct.browse(medicament_id)

                if not medicament:
                    raise Exception(
                        "El medicamento suministrado al residente no existe en el sistema"
                    )

                inventory = MedicationInventory.search(
                    [
                        ("resident_id", "=", resident.id),
                        ("cat_uom_id", "=", cat_uom.id),
                        ("medicament_id", "=", medicament.id),
                    ],
                    limit=1,
                )
                # - Chequear que existe un inventario para Medicamento-Rsidente-Categoria
                if not inventory:
                    raise Exception(
                        "El sistema no cuenta con níngún inventario asociado al residente \
del cual pueda suministrar el medicamento especificado"
                    )

                indication_medication = None

                if indication_medication_id and indication_medication_id != -1:
                    indication_medication = MedicalMedication.browse(
                        indication_medication_id
                    )

                    if not indication_medication:
                        raise Exception(
                            f"No existe una indicación médica con identificador: {indication_medication_id}"
                        )

                    if indication_medication:
                        med_id = str(
                            indication_medication.resident_id.id).strip()
                        res_id = str(resident_id).strip()
                        if med_id != res_id:
                            raise Exception(
                                f"La indicación médica con identificador: {indication_medication.resident_id != resident_id} no esta realacionada con el residente con el identificador: {resident_id}"
                            )

                # - Realizar conversion
                if inventory.uom_id != uom:
                    dosage_amount = uom._compute_quantity(
                        dosage_amount, inventory.uom_id
                    )

                # - Actualizar el inventario
                new_quantity = inventory.available_quantity - dosage_amount
                if new_quantity < 0:
                    raise Exception(
                        "La cantidad de medicamento disponible en el inventario es insuficiente para realizar el suministro al residente")

                inventory.write(
                    {
                        "available_quantity": new_quantity,
                    }
                )
                reason = "El registro de la extracción de esa cantidad vino a traves de una petición del API de Serena-Care"
                if indication_medication:
                    reason = f"Se extrajo esta cantidad para suministrarselo al residente como parte del cumplimiento de una indicación medica. {indication_medication.note}"
                date_adjust = self._adjust_timezone(user, data["date"])
                # - Registrar la operación de salida
                id_indication = False
                if indication_medication_id and indication_medication_id != -1:
                    id_indication = indication_medication_id
                record_oper = OperationInventory.create(
                    {
                        "quantity": dosage_amount,
                        "uom_id": uom.id,
                        "reason": reason,
                        "operation_type": "out",
                        "medication_inventory_id": inventory.id,
                        "user_id": user.id,
                        "family_id": False,
                        "date": date_adjust,
                        "indication_medication_id": id_indication,
                    }
                )
                if record_oper:
                    answer = {
                        "id": record_oper.id,
                        "date": self._convert_timezone(user, record_oper.date),
                        "user_id": record_oper.user_id.id,
                        "user_name": record_oper.user_id.name,
                        "resident_id": record_oper.medication_inventory_id.resident_id.id,
                        "resident_name": record_oper.medication_inventory_id.resident_id.name,
                    }
                answer = {
                    "status": "success",
                    "message": "Registro creado existosamente",
                    "data": answer,
                }
                _logger.info(f"Response: {answer}")
                # return Response( answer,headers={"Content-Type": "application/json"}, )
                return answer
        except Exception as e:
            return self._handle_error(e)
