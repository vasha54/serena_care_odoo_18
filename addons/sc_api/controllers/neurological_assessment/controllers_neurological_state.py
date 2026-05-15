import json
import math

from odoo import _, http
from odoo.http import Response, request

from ..controllers_base import BaseAPIController


class NeurologicalStateAPIController(BaseAPIController):
    
    def doc_get_list_neurological_state(self):
        """
        Documentación Swagger para el método get_list_neurological_state
        
        Returns:
            dict: Documentación Swagger para el endpoint de listado de los niveles de anomalía
        """
        return {
            "tags": ["Evaluación Neurológica"],
            "summary": "Lista los estados neurológicos",
            "description": (
                "Retorna un listado de todos los estados neurológicos disponibles en el sistema "
                "con su ID y nombre. Usado en el proceso de registrar una anomalía de un residente."
            ),
            "responses": {
                "200": {
                    "description": "Listado de los estados neurológicos obtenido exitosamente",
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
                                        "description": "Arreglo de objetos con información de los estados neurológicos",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "id": {
                                                    "type": "integer",
                                                    "description": "ID único del estado neurológico",
                                                    "example": 1
                                                },
                                                "name": {
                                                    "type": "string",
                                                    "description": "Nombre del estado neurológico",
                                                    "example": "Moderado"
                                                },
                                                "color": {
                                                    "type": "string",
                                                    "description": "Color del estado neurológico en hexadecimal",
                                                    "example": "#234589"
                                                },
                                                "description": {
                                                    "type": "string",
                                                    "description": "Description del estado neurológico",
                                                    "example": "El paciente esta alerta"
                                                },
                                                "acronym": {
                                                    "type": "string",
                                                    "description": "Acrónimo del estado neurológico",
                                                    "example": "A"
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
        "/api_serena/v1/list_neurological_state",
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
    )
    def get_list_neurological_state(self, **kwargs):
        try:
            data = (
                request.env["neurological.state"]
                .sudo()
                .search_read(
                    [('active','=',True)],
                    ["id", "name", "color", "description", "acronym"],
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