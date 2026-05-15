import json
import math

from odoo import _, http
from odoo.http import Response, request

from ..controllers_base import BaseAPIController


class NutritionLevelAPIController(BaseAPIController):
    
    def doc_get_list_nutrition_level(self):
        """
        Documentación Swagger para el método get_list_nutrition_level
        
        Returns:
            dict: Documentación Swagger para el endpoint de listado de los niveles de alimentos
        """
        return {
            "tags": ["Alimentos"],
            "summary": "Lista los niveles de alimentación",
            "description": (
                "Retorna un listado de todas los niveles de alimentación disponibles en el sistema "
                "con su ID y nombre. Usado en el proceso de registrar una alimentación de un residente."
            ),
            "responses": {
                "200": {
                    "description": "Listado de los niveles de alimentación obtenido exitosamente",
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
                                        "description": "Arreglo de objetos con información de los niveles de alimentación",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "id": {
                                                    "type": "integer",
                                                    "description": "ID único del nivel de alimentos",
                                                    "example": 1
                                                },
                                                "name": {
                                                    "type": "string",
                                                    "description": "Nombre del nivel de alimentos",
                                                    "example": "Moderado"
                                                },
                                                "percent": {
                                                    "type": "double",
                                                    "description": "Porciento que indica el porcente de alimentos injeridos por el paciente a partir de la ración suministrada",
                                                    "example": 50.0
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
        "/api_serena/v1/list_nutrition_level",
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
    )
    def get_list_nutrition_level(self, **kwargs):
        try:
            data = (
                request.env["nutrition.level"]
                .sudo()
                .search_read(
                    [],
                    ["id", "name", "percent"],
                )
            ) 
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