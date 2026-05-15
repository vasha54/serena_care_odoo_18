import json
import math

from odoo import _, http
from odoo.http import Response, request

from ..controllers_base import BaseAPIController


class MoodStateAPIController(BaseAPIController):
    
    def doc_get_list_mood_state(self):
        """
        Documentación Swagger para el método get_list_mood_state

        Returns:
            dict: Documentación Swagger para el endpoint de listar estados de ánimo
        """
        return {
            "tags": ["Evaluación de Ánimo"],
            "summary": "Obtener lista de estados de ánimo activos",
            "description": """
            Endpoint público para obtener la lista de todos los estados de ánimo activos 
            disponibles en el sistema. No requiere autenticación.

            **Características:**
            - Devuelve solo estados de ánimo marcados como activos
            - Ordena los resultados por el campo 'order'
            - Incluye información sobre si cada estado tiene imagen y su URL correspondiente
            - La URL de la imagen se genera dinámicamente basada en el ID del estado

            **Nota:** Este endpoint es público y no requiere token de autenticación.
            """,
            "parameters": [],
            "responses": {
                "200": {
                    "description": "Lista de estados de ánimo obtenida exitosamente",
                    "headers": {
                        "Content-Type": {
                            "type": "string",
                            "description": "Tipo de contenido de la respuesta (application/json)",
                        }
                    },
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
                                        "example": "Datos obtenidos correctamente",
                                        "description": "Mensaje descriptivo del resultado",
                                    },
                                    "data": {
                                        "type": "array",
                                        "description": "Lista de estados de ánimo activos",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "id": {
                                                    "type": "integer",
                                                    "description": "Identificador único del estado de ánimo",
                                                    "example": 1,
                                                },
                                                "name": {
                                                    "type": "string",
                                                    "description": "Nombre del estado de ánimo",
                                                    "example": "Feliz",
                                                },
                                                "order": {
                                                    "type": "integer",
                                                    "description": "Orden de visualización del estado de ánimo",
                                                    "example": 1,
                                                },
                                                "image": {
                                                    "type": "boolean",
                                                    "description": "Indica si el estado de ánimo tiene una imagen asociada",
                                                    "example": True,
                                                },
                                                "image_url": {
                                                    "type": "string",
                                                    "format": "uri",
                                                    "description": "URL completa de la imagen del estado de ánimo (solo si image es true)",
                                                    "example": "http://localhost:8069/public/image/mood_state/1",
                                                    "nullable": True,
                                                },
                                            },
                                            "required": [
                                                "id",
                                                "name",
                                                "order",
                                                "image",
                                                "image_url",
                                            ],
                                        },
                                    },
                                },
                                "required": ["status", "message", "data"],
                            },
                            "example": {
                                "status": "success",
                                "message": "Datos obtenidos correctamente",
                                "data": [
                                    {
                                        "id": 1,
                                        "name": "Feliz",
                                        "order": 1,
                                        "image": True,
                                        "image_url": "http://localhost:8069/public/image/mood_state/1",
                                    },
                                    {
                                        "id": 2,
                                        "name": "Triste",
                                        "order": 2,
                                        "image": True,
                                        "image_url": "http://localhost:8069/public/image/mood_state/2",
                                    },
                                    {
                                        "id": 3,
                                        "name": "Enojado",
                                        "order": 3,
                                        "image": False,
                                        "image_url": None,
                                    },
                                ],
                            },
                        }
                    },
                },
                "400": {
                    "description": "Solicitud incorrecta",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "status": {"type": "string", "example": "error"},
                                    "message": {
                                        "type": "string",
                                        "example": "Error en la solicitud",
                                    },
                                    "data": {"type": "null", "example": None},
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
                                    "data": {"type": "null", "example": None},
                                },
                            }
                        }
                    },
                },
            },
            "security": [],
        }

    @http.route(
        "/api_serena/v1/list_mood_state",
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
    )
    def get_list_mood_state(self, **kwargs):
        try:
            data = (
                request.env["mood.state"]
                .sudo()
                .search_read(
                    domain=[("active", "=", True)],
                    fields=["id", "name", "order", "image"],
                    order="order",
                )
            )

            base_url = (
                request.env["ir.config_parameter"].sudo().get_param("web.base.url")
            )

            for d in data:
                if d.get("image"):
                    d["image"] = True
                    d["image_url"] = f"{base_url}/public/image/mood_state" f"/{d['id']}"
                else:
                    d["image"] = False
                    d["image_url"] = None

            answer = {
                "status": "success",
                "message": "Datos obtenidos correctamente",
                "data": data,
            }
            return Response(
                json.dumps(answer), headers={"Content-Type": "application/json"}
            )
        except Exception as e:
            return self._handle_error_get(e)
