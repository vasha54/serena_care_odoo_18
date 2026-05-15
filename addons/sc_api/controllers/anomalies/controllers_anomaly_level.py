import json
import math

from odoo import _, http
from odoo.http import Response, request

from ..controllers_base import BaseAPIController


class AnomalyLevelAPIController(BaseAPIController):
    
    def doc_get_list_anomaly_level(self):
        """
        Documentación Swagger para el método get_list_anomaly_level
        
        Returns:
            dict: Documentación Swagger para el endpoint de listado de los niveles de anomalía
        """
        return {
            "tags": ["Anomalías"],
            "summary": "Lista los niveles de anomalía",
            "description": (
                "Retorna un listado de todas los niveles de anomalía disponibles en el sistema "
                "con su ID y nombre. Usado en el proceso de registrar una anomalía de un residente."
            ),
            "responses": {
                "200": {
                    "description": "Listado de los niiveles de anomalía obtenido exitosamente",
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
                                        "description": "Arreglo de objetos con información de los niveles de anomalía",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "id": {
                                                    "type": "integer",
                                                    "description": "ID único del nivel de anomalía",
                                                    "example": 1
                                                },
                                                "name": {
                                                    "type": "string",
                                                    "description": "Nombre del nivel de anomalía",
                                                    "example": "Moderado"
                                                },
                                                "color": {
                                                    "type": "string",
                                                    "description": "Color del nivel de anomalía en hexadecimal",
                                                    "example": "#234589"
                                                },
                                                "sequence": {
                                                    "type": "integer",
                                                    "description": "Orden de "
                                                                   "la "
                                                                   "secuencia de los diferentes niveles de anomalías",
                                                    "example": 2
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
        "/api_serena/v1/list_anomaly_level",
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
    )
    def get_list_anomaly_level(self, **kwargs):
        try:
            data = (
                request.env["anomaly.level"]
                .sudo()
                .search_read(
                    domain=[('active','=',True)],
                    fields=["id", "name", "color", "sequence"],
                    order="sequence",
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
