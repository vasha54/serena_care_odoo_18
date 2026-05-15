import json
import math

from odoo import _, http
from odoo.http import Response, request

from ..controllers_base import BaseAPIController


class ActivityRecreationalTypeAPIController(BaseAPIController):
    
    def doc_get_list_recreational_activity_type(self):
        """
        Documentación Swagger para el método get_list_residence_login
        
        Returns:
            dict: Documentación Swagger para el endpoint de listado de los tipos de actividades recreativas
        """
        return {
            "tags": ["Actividades Recreativas"],
            "summary": "Lista los tipos de actividades recreativas",
            "description": (
                "Retorna un listado de todas los tipos de actividades recreativas disponibles en el sistema "
                "con su ID y nombre. Usado en el proceso de registrar una actividad recreativa donde se involucre "
                "uno o más residentes."
            ),
            "responses": {
                "200": {
                    "description": "Listado de tipos de actividades recreativas obtenido exitosamente",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "status": {
                                        "type": "string",
                                        "example": "success",
                                        "description": "Indica si la consulta se ejecutó correctamente"
                                    },
                                    "message": {
                                        "type": "string",
                                        "example": "Datos obtenidos correctamente",
                                        "description": "Mensaje acerca de la ejecución de la consulta"
                                    },
                                    "data": {
                                        "type": "array",
                                        "description": "Arreglo de objetos con información de tipos de actividades recreativas",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "id": {
                                                    "type": "integer",
                                                    "description": "ID único del tipo de actividad recreativa",
                                                    "example": 1
                                                },
                                                "name": {
                                                    "type": "string",
                                                    "description": "Nombre del tipo de actividad recreativa",
                                                    "example": "Club de lectura"
                                                },
                                                "image": {
                                                    "type": "",
                                                    "description": "Verdadero si el tipo de activades posee una imagen y falso en caso contrario",
                                                    "example": True,
                                                },
                                                "image_url": {
                                                    "type": "string",
                                                    "description": "Url de la imagen que representa la actividad si lo tiene",
                                                    "example": "http://<dominio.com>/web/image/public/resident/24/image_1920",
                                                },
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "400": {
                    "description": "Parámetros inválidos en la solicitud"
                },
                "500": {
                    "description": "Error interno del servidor"
                }
            },
            "parameters": [],
            "security": [{"public": []}]
        }

    @http.route(
        "/api_serena/v1/list_recreational_activity_type",
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
    )
    def get_list_recreational_activity_type(self, **kwargs):
        try:
            data = (
                request.env["nomenclature.activity.type"]
                .sudo()
                .search_read(
                    [('active', '=', True)],
                    ["id", "name", "image"],
                )
            )
            base_url = (
                        request.env["ir.config_parameter"].sudo().get_param("web.base.url")
                    )
            for d in data:
                if d.get("image"):
                    d["image"] = True
                    d["image_url"] = f"{base_url}/public/image/recreational_activity_type/{d['id']}"
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
