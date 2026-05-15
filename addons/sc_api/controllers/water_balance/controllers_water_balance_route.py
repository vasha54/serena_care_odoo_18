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


class WaterBalanceRouteController(BaseAPIController):

    def doc_get_list_water_balance_route(self):
        """
        Documentación Swagger para el método get_list_water_balance_route
        
        Returns:
            dict: Documentación Swagger para el endpoint de listar rutas de balance hídrico
        """
        return {
            "tags": ["Balance Hídrico"],
            "summary": "Obtener listado de vías de ingreso/egreso de balance hídrico",
            "description": "Retorna una lista de todas las vías de ingreso/egreso de balance hídrico registradas en el sistema. Cada registro incluye el ID y nombre de la ruta.",
            "responses": {
                "200": {
                    "description": "OK",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "status": {
                                        "type": "string",
                                        "example": "success"
                                    },
                                    "message": {
                                        "type": "string",
                                        "example": "Datos obtenidos correctamente"
                                    },
                                    "data": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "id": {
                                                    "type": "integer",
                                                    "description": "ID único de la ruta",
                                                    "example": 1
                                                },
                                                "name": {
                                                    "type": "string",
                                                    "description": "Nombre de la ruta",
                                                    "example": "Orina"
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
                    "description": "Error en la solicitud",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "status": {
                                        "type": "string",
                                        "example": "error"
                                    },
                                    "message": {
                                        "type": "string",
                                        "example": "Descripción del error"
                                    }
                                }
                            }
                        }
                    }
                },
                "500": {
                    "description": "Error interno del servidor",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "status": {
                                        "type": "string",
                                        "example": "error"
                                    },
                                    "message": {
                                        "type": "string",
                                        "example": "Error interno del servidor"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        } 

    @http.route(
        "/api_serena/v1/list_water_balance_route",
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
    )
    def get_list_water_balance_route(self, **kwargs):
        try:
            data = (
                request.env["water.balance.route"]
                .sudo()
                .search_read(
                    [],
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
