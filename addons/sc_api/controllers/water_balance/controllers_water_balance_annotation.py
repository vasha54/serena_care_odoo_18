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


class WaterBalanceAnnotationController(BaseAPIController):
    
    def doc_register_water_balance_annotation(self):
        """
        Documentación Swagger para el método register_water_balance_annotation

        Returns:
            dict: Documentación Swagger para el endpoint de registrar anotación de balance hídrico
        """
        return {
            "tags": ["Balance Hídrico"],
            "summary": "Registrar anotación de balance hídrico",
            "description": """
            Endpoint para registrar una nueva anotación de balance hídrico para un residente específico. 
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
                                "description": "ID del residente",
                                "example": 123,
                            },
                            "route_id": {
                                "type": "integer",
                                "description": "ID de la ruta",
                                "example": 456,
                            },
                            "type_annotation": {
                                "type": "string",
                                "description": "Tipo de anotación (income/expense)",
                                "enum": ["income", "expense"],
                                "example": "income",
                            },
                            "quantity": {
                                "type": "number",
                                "format": "float",
                                "description": "Cantidad de agua",
                                "example": 2.5,
                            },
                            "notes": {
                                "type": "string",
                                "description": "Notas adicionales (opcional)",
                                "example": "Ingesta de agua durante la mañana",
                            },
                            "date": {
                                "type": "string",
                                "format": "date-time",
                                "description": "Fecha y hora que se hace la anotación en formato '%Y-%m-%d %H:%M:%S'",
                                "example": "2025-08-20 10:00:00"
                            }
                        },
                        "required": [
                            "resident_id",
                            "route_id",
                            "type_annotation",
                            "quantity",
                            "date",
                        ],
                    },
                },
            ],
            "responses": {
                "200": {
                    "description": "Anotación registrada exitosamente",
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
                                                "description": "ID del registro creado",
                                                "example": 789,
                                            },
                                            "date": {
                                                "type": "string",
                                                "format": "date-time",
                                                "description": "Fecha de creación en formato ISO",
                                                "example": "2023-10-15T14:30:00Z",
                                            },
                                            "user_id": {
                                                "type": "integer",
                                                "description": "ID del usuario que creó el registro",
                                                "example": 55,
                                            },
                                            "user_name": {
                                                "type": "string",
                                                "description": "Nombre del usuario",
                                                "example": "Juan Pérez",
                                            },
                                            "resident_id": {
                                                "type": "integer",
                                                "description": "ID del residente",
                                                "example": 123,
                                            },
                                            "resident_name": {
                                                "type": "string",
                                                "description": "Nombre del residente",
                                                "example": "María García",
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
                                "example": "El tipo de anotación no se corresponde con las permitidas en el balance hídrico",
                            },
                            "data": {"type": "null", "example": None},
                        },
                    },
                },
                "401": {
                    "description": "No autorizado (token inválido o expirado)",
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
                    "description": "Acceso denegado",
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
        }

    def doc_list_wbalance_annotation_this_resident_range(self):
        """
        Documentación Swagger para el método list_wbalance_annotation_this_resident_range

        Returns:
            dict: Documentación Swagger para el endpoint de listar anotaciones por rango de fechas
        """
        return {
            "tags": ["Balance Hídrico"],
            "summary": "Obtener anotaciones de balance hídrico por rango de fechas",
            "description": """
            Endpoint para obtener las anotaciones de balance hídrico de un residente dentro de un rango de fechas específico. 
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
                                "description": "ID del residente",
                                "example": 123,
                            },
                            "date_start": {
                                "type": "string",
                                "format": "date",
                                "description": "Fecha de inicio (YYYY-MM-DD)",
                                "example": "2023-10-01",
                            },
                            "date_end": {
                                "type": "string",
                                "format": "date",
                                "description": "Fecha de fin (YYYY-MM-DD)",
                                "example": "2023-10-15",
                            },
                        },
                        "required": ["resident_id", "date_start", "date_end"],
                    },
                },
            ],
            "responses": {
                "200": {
                    "description": "Lista de anotaciones obtenida exitosamente",
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
                                        "description": "Listado de objetos donde cada objeto representa una anotiación ",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "id": {
                                                    "type": "integer",
                                                    "description": "ID del registro",
                                                    "example": 789,
                                                },
                                                "date": {
                                                    "type": "string",
                                                    "description": "Fecha de creación (YYYY-MM-DD HH:MM)",
                                                    "example": "2023-10-15 14:30:00",
                                                },
                                                "user": {
                                                    "type": "string",
                                                    "description": "Información del usuario",
                                                    "example": "Juan Pérez (ID: 55)",
                                                },
                                                "resident": {
                                                    "type": "string",
                                                    "description": "Información del residente",
                                                    "example": "María García (ID: 123)",
                                                },
                                                "type": {
                                                    "type": "string",
                                                    "description": "Tipo de anotación (traducido)",
                                                    "example": "Ingreso",
                                                },
                                                "notes": {
                                                    "type": "string",
                                                    "description": "Notas adicionales",
                                                    "example": "Ingesta de agua durante la mañana",
                                                },
                                                "quantity": {
                                                    "type": "number",
                                                    "format": "float",
                                                    "description": "Cantidad de agua",
                                                    "example": 2.5,
                                                },
                                                "route_data": {
                                                    "type": "object",
                                                    "properties": {
                                                        "id": {
                                                            "type": "integer",
                                                            "description": "ID único de la ruta",
                                                            "example": 1,
                                                        },
                                                        "name": {
                                                            "type": "string",
                                                            "description": "Nombre de la ruta",
                                                            "example": "Orina",
                                                        },
                                                    },
                                                    "description": "Información de la vía de ingreso/egreso, (id,nombre)",
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
                                "example": "El rango de fecha seleccionado es incorrecto",
                            },
                            "data": {"type": "null", "example": None},
                        },
                    },
                },
                "401": {
                    "description": "No autorizado (token inválido o expirado)",
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
                    "description": "Acceso denegado",
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
        }

    def doc_list_wbalance_annotation_this_resident_all(self):
        """
        Documentación Swagger para el método list_wbalance_annotation_this_resident_all

        Returns:
            dict: Documentación Swagger para el endpoint de listar todas las anotaciones
        """
        return {
            "tags": ["Balance Hídrico"],
            "summary": "Obtener todas las anotaciones de balance hídrico de un residente",
            "description": """
            Endpoint para obtener todas las anotaciones de balance hídrico de un residente específico. Requiere autenticación 
            JWT válida.
          
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
                                "description": "ID del residente",
                                "example": 123,
                            }
                        },
                        "required": ["resident_id"],
                    },
                },
            ],
            "responses": {
                "200": {
                    "description": "Lista de anotaciones obtenida exitosamente",
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
                                        "description": "Listado de objetos donde cada objeto representa una anotiación ",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "id": {
                                                    "type": "integer",
                                                    "description": "ID del registro",
                                                    "example": 789,
                                                },
                                                "date": {
                                                    "type": "string",
                                                    "description": "Fecha de creación (YYYY-MM-DD HH:MM)",
                                                    "example": "2023-10-15 14:30:00",
                                                },
                                                "user": {
                                                    "type": "string",
                                                    "description": "Información del usuario",
                                                    "example": "Juan Pérez (ID: 55)",
                                                },
                                                "resident": {
                                                    "type": "string",
                                                    "description": "Información del residente",
                                                    "example": "María García (ID: 123)",
                                                },
                                                "type": {
                                                    "type": "string",
                                                    "description": "Tipo de anotación (traducido)",
                                                    "example": "Ingreso",
                                                },
                                                "notes": {
                                                    "type": "string",
                                                    "description": "Notas adicionales",
                                                    "example": "Ingesta de agua durante la mañana",
                                                },
                                                "quantity": {
                                                    "type": "number",
                                                    "format": "float",
                                                    "description": "Cantidad de agua",
                                                    "example": 2.5,
                                                },
                                                "route_data": {
                                                    "type": "object",
                                                    "properties": {
                                                        "id": {
                                                            "type": "integer",
                                                            "description": "ID único de la ruta",
                                                            "example": 1,
                                                        },
                                                        "name": {
                                                            "type": "string",
                                                            "description": "Nombre de la ruta",
                                                            "example": "Orina",
                                                        },
                                                    },
                                                    "description": "Información de la vía de ingreso/egreso, (id,nombre)",
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
                            "data": {"type": "null", "example": None},
                        },
                    },
                },
                "401": {
                    "description": "No autorizado (token inválido o expirado)",
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
                    "description": "Acceso denegado",
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
        }

    @http.route(
        "/api_serena/v1/register_water_balance_annotation",
        type="json",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def register_water_balance_annotation(self, **post):
        try:
            parameters = [
                "resident_id",
                "route_id",
                "type_annotation",
                "quantity",
                "date",
            ]
            token = self._get_token()
            payload = self._get_payload(token)
            data = self._get_json_data(request.httprequest.data)
            self._check_existence_parameters(parameters, data)

            # Chequear que el tipo de anotación del balance hídrico sea de la
            # permitidas
            if data["type_annotation"] not in ["income", "expense"]:
                raise Exception(
                    "El tipo de anotación no se corresponde con \
las permitidas en el balance hídrico"
                )

            current_db = request.env.cr.dbname
            user_id = payload["user_id"]
            residence_id = payload["residence_id"]
            resident_id = data["resident_id"]

            answer = {}
            # Usar Registry directamente como recomienda el warning
            registry = Registry(current_db)

            with registry.cursor() as cr:
                env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
                WaterBalanceAnnotation = env["water.balance.annotation"].sudo()
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
                if not self._check_user_permissions(user, 'water.balance.annotation', self.CAN_CREATE, env):
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
                date_adjust = self._adjust_timezone(user, data['date'])
                # Registrar la medición del balance hídrico
                record_wb = WaterBalanceAnnotation.create(
                    {
                        "resident_id": resident.id,
                        "user_id": user.id,
                        "route_id": data["route_id"],
                        "type_annotation": data["type_annotation"],
                        "quantity": data["quantity"],
                        "notes": data.get("notes", ""),
                        "date": date_adjust
                    }
                )
                if record_wb:
                    answer = {
                        "id": record_wb.id,
                        "date": self._convert_to_iso(record_wb.date),
                        "user_id": record_wb.user_id.id,
                        "user_name": record_wb.user_id.name,
                        "resident_id": record_wb.resident_id.id,
                        "resident_name": record_wb.resident_id.name,
                    }

            answer = {
                "status": "success",
                "message": "Registro creado existosamente",
                "data": answer,
            }
            return answer
            # return Response(
            #     answer,
            #     headers={"Content-Type": "application/json"},
            # )

        except Exception as e:
            return self._handle_error(e)

    @http.route(
        "/api_serena/v1/list_wbalance_annotation_this_resident_range",
        type="json",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def list_wbalance_annotation_this_resident_range(self, **post):
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
                WaterBalanceAnnotation = env["water.balance.annotation"].sudo()
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
                if not self._check_user_permissions(user, 'water.balance.annotation', self.CAN_READ, env):
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

                # Listar todas las mediciones del balance hídrico del residente
                # en el rango de fecha
                answer = []
                records_wb = WaterBalanceAnnotation.search_read(
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
                        "type_annotation",
                        "route_data",
                        "notes",
                        "quantity",
                    ],
                    order="date DESC",
                )

                if records_wb:
                    selection_dict = dict(
                        WaterBalanceAnnotation._fields["type_annotation"].selection
                    )
                    for wb in records_wb:
                        type_label = selection_dict.get(wb["type_annotation"], "")
                        answer.append(
                            {
                                "date": self._convert_timezone(user,wb["date"])
                                if wb["date"]
                                else "",
                                "user": wb["user_data"],
                                "resident": wb["resident_data"],
                                "type": type_label,
                                "notes": wb["notes"] or "Sin detalles",
                                "quantity": wb["quantity"],
                                "route": wb["route_data"],
                                "id": wb["id"],
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
        "/api_serena/v1/list_wbalance_annotation_this_resident_all",
        type="json",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def list_wbalance_annotation_this_resident_all(self, **post):
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
                WaterBalanceAnnotation = env["water.balance.annotation"].sudo()
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
                if not self._check_user_permissions(user, 'water.balance.annotation', self.CAN_READ, env):
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

                # Listar todas las mediciones del balance hídrico del residente
                answer = []
                records_wb = WaterBalanceAnnotation.search_read(
                    domain=[("resident_id", "=", resident_id)],
                    fields=[
                        "id",
                        "date",
                        "resident_data",
                        "user_data",
                        "type_annotation",
                        "route_data",
                        "notes",
                        "quantity",
                    ],
                    order="date DESC",
                )

                if records_wb:
                    selection_dict = dict(
                        WaterBalanceAnnotation._fields["type_annotation"].selection
                    )
                    for wb in records_wb:
                        type_label = selection_dict.get(wb["type_annotation"], "")
                        answer.append(
                            {
                                "date": self._convert_timezone(user,wb["date"])
                                if wb["date"]
                                else "",
                                "user": wb["user_data"],
                                "resident": wb["resident_data"],
                                "type": type_label,
                                "notes": wb["notes"] or "Sin detalles",
                                "quantity": wb["quantity"],
                                "route": wb["route_data"],
                                "id": wb["id"],
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
