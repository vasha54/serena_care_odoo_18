import json
import math

from odoo import _, http
from odoo.http import Response, request

from ..controllers_base import BaseAPIController


class EvacuationTypeAPIController(BaseAPIController):

    def doc_get_list_evacuation_type(self):
        """
        Documentación Swagger para el método get_list_evacuation_type

        Returns:
            dict: Documentación Swagger para el endpoint de listado de los tipos de higiene
        """
        return {
            "tags": ["Higiene"],
            "summary": "Lista los tipos de evacuación",
            "description": (
                "Retorna un listado de todos  tipos de evacuación disponibles "
                "en el sistema "
                "con su ID y nombre. Usado en el proceso de registrar un chequeo de higiene de un residente."
            ),
            "responses": {
                "200": {
                    "description": "Listado de los tipos de evacuaciones "
                                   "obtenido exitosamente",
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
                                        "description": "Arreglo de objetos "
                                                       "con información de "
                                                       "los tipos de "
                                                       "evacuación",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "id": {
                                                    "type": "integer",
                                                    "description": "ID único "
                                                                   "del tipo "
                                                                   "de "
                                                                   "evacuación",
                                                    "example": 1
                                                },
                                                "name": {
                                                    "type": "string",
                                                    "description": "Nombre "
                                                                   "del tipo "
                                                                   "de "
                                                                   "evacuación",
                                                    "example": "Salchichas con grietas"
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
        "/api_serena/v1/list_evacuation_type",
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
    )
    def get_list_evacuation_type(self, **kwargs):
        try:
            data = (
                request.env["evacuation.type"]
                .sudo()
                .search_read(
                    domain = [("active","=",True)],
                    fields = ["id", "name"],
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
