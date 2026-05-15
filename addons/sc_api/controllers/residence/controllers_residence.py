import json
import math

from odoo import _, http
from odoo.http import Response, request

from ..controllers_base import BaseAPIController


class ResidenceAPIController(BaseAPIController):
    
    def doc_get_list_residence_login(self):
        """
        Documentación Swagger para el método get_list_residence_login
        
        Returns:
            dict: Documentación Swagger para el endpoint de listado de residencias
        """
        return {
            "tags": ["Residencias"],
            "summary": "Lista de residencias para selección en login",
            "description": (
                "Retorna un listado de todas las residencias disponibles en el sistema "
                "con su ID y nombre. Usado en el proceso de login para que los usuarios "
                "seleccionen su residencia."
            ),
            "responses": {
                "200": {
                    "description": "Listado de residencias obtenido exitosamente",
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
                                        "description": "Arreglo de objetos con información de residencias",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "id": {
                                                    "type": "integer",
                                                    "description": "ID único de la residencia",
                                                    "example": 1
                                                },
                                                "name": {
                                                    "type": "string",
                                                    "description": "Nombre de la residencia",
                                                    "example": "Casa Serena Polanco"
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
        "/api_serena/v1/list_residence_login",
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
    )
    def get_list_residence_login(self, **kwargs):
        try:
            data = (
                request.env["residence_house"]
                .sudo()
                .search_read(
                    [('active','=',True),('is_deleted','=',False)],
                    ["id", "name"],
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