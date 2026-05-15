import json
import math

from odoo import _, http
from odoo.http import Response, request

from ..controllers_base import BaseAPIController


class CategoryUoMController(BaseAPIController):
    
    def doc_get_list_category_uom(self):
        """
        Documentación Swagger para el método get_list_category_uom
        
        Returns:
            dict: Documentación Swagger para el endpoint de categorías de UoM
        """
        return {
            "tags": ["Unidades de Medida"],
            "summary": "Obtener categorías de unidades de medida",
            "description": (
                "Obtiene el listado de todas las categorías en que se organizan "
                "las unidades de medidas gestionadas por Serena-Care (is_uom_sc=True). "
                "Las categorías incluyen información básica como ID y nombre."
            ),
            "responses": {
                "200": {
                    "description": "Lista de categorías obtenida exitosamente",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "status": {
                                        "type": "string",
                                        "example": "success",
                                        "description": "Indica si la consulta se ejecutó correctamente (success) o si ocurrió un error (error)"
                                    },
                                    "message": {
                                        "type": "string",
                                        "example": "Datos obtenidos correctamente",
                                        "description": "Mensaje acerca de la ejecución de la consulta"
                                    },
                                    "data": {
                                        "type": "array",
                                        "description": "Arreglo de objetos con información de categorías",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "id": {
                                                    "type": "integer",
                                                    "description": "ID único de la categoría",
                                                    "example": 31
                                                },
                                                "name": {
                                                    "type": "string",
                                                    "description": "Nombre de la categoría",
                                                    "example": "Unidades"
                                                }
                                            }
                                        }
                                    }
                                }
                            },
                            "example": {
                                "status": "success",
                                "message": "Datos obtenidos correctamente",
                                "data": [
                                    {"id": 31, "name": "Unidades"},
                                    {"id": 32, "name": "Tiempo"},
                                    {"id": 33, "name": "Medicamentos"},
                                    {"id": 34, "name": "Peso"},
                                    {"id": 35, "name": "Volumen"},
                                    {"id": 36, "name": "Longitud"}
                                ]
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
                                    },
                                    "data": {
                                        "type": "null",
                                        "example": None
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
                                    },
                                    "data": {
                                        "type": "null",
                                        "example": None
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "parameters": [],
            "security": [{"public": []}]
        }


    @http.route(
        "/api_serena/v1/list_category_uom",
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
    )
    def get_list_category_uom(self, **kwargs):
        try:
            data = (
                request.env["uom.category"]
                .sudo()
                .search_read(
                    [('is_uom_sc','=',True)],
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