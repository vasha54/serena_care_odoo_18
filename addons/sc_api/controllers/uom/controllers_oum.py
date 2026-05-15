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


class UoMController(BaseAPIController):
    
    def doc_get_list_all_uom(self):
        """
        Documentación Swagger para el método get_list_all_uom
        
        Returns:
            dict: Documentación Swagger para el endpoint de todas las UoM
        """
        return {
            "tags": ["Unidades de Medida"],
            "summary": "Obtener todas las unidades de medida",
            "description": (
                "Obtiene el listado de todas las unidades de medida gestionadas "
                "por Serena-Care (is_uom_sc=True). Incluye información básica "
                "como ID, nombre y categoría."
            ),
            "responses": {
                "200": {
                    "description": "Lista de unidades de medida obtenida exitosamente",
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
                                        "description": "Arreglo de objetos con información de unidades de medida",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "id": {
                                                    "type": "integer",
                                                    "description": "ID único de la unidad de medida",
                                                    "example": 139
                                                },
                                                "name": {
                                                    "type": "string",
                                                    "description": "Nombre de la unidad de medida",
                                                    "example": "Kilolitro"
                                                },
                                                "category": {
                                                    "type": "object",
                                                    "description": "Información de la categoría",
                                                    "properties": {
                                                        "id": {
                                                            "type": "integer",
                                                            "description": "ID de la categoría",
                                                            "example": 35
                                                        },
                                                        "name": {
                                                            "type": "string",
                                                            "description": "Nombre de la categoría",
                                                            "example": "Volumen"
                                                        }
                                                    }
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
                                    {
                                        "id": 139,
                                        "name": "Kilolitro",
                                        "category": {"id": 35, "name": "Volumen"}
                                    },
                                    {
                                        "id": 140,
                                        "name": "Hectolitro", 
                                        "category": {"id": 35, "name": "Volumen"}
                                    }
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

    def doc_get_list_uom_this_category(self):
        """
        Documentación Swagger para el método get_list_uom_this_category
        
        Returns:
            dict: Documentación Swagger para el endpoint de UoM por categoría
        """
        return {
            "tags": ["Unidades de Medida"],
            "summary": "Obtener unidades de medida por categoría",
            "description": (
                "Obtiene el listado de todas las unidades de medida asociadas a una "
                "categoría específica gestionadas por Serena-Care (is_uom_sc=True). "
                "Requiere el ID de la categoría en el cuerpo de la solicitud."
            ),
            "responses": {
                "200": {
                    "description": "Lista de unidades de medida obtenida exitosamente",
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
                                        "description": "Arreglo de objetos con información de unidades de medida",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "id": {
                                                    "type": "integer",
                                                    "description": "ID único de la unidad de medida",
                                                    "example": 139
                                                },
                                                "name": {
                                                    "type": "string",
                                                    "description": "Nombre de la unidad de medida",
                                                    "example": "Kilolitro"
                                                },
                                                "category": {
                                                    "type": "object",
                                                    "description": "Información de la categoría",
                                                    "properties": {
                                                        "id": {
                                                            "type": "integer",
                                                            "description": "ID de la categoría",
                                                            "example": 35
                                                        },
                                                        "name": {
                                                            "type": "string",
                                                            "description": "Nombre de la categoría",
                                                            "example": "Volumen"
                                                        }
                                                    }
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
                                    {
                                        "id": 139,
                                        "name": "Kilolitro",
                                        "category": {"id": 35, "name": "Volumen"}
                                    },
                                    {
                                        "id": 140,
                                        "name": "Hectolitro",
                                        "category": {"id": 35, "name": "Volumen"}
                                    },
                                    {
                                        "id": 141,
                                        "name": "Decalitro",
                                        "category": {"id": 35, "name": "Volumen"}
                                    }
                                ]
                            }
                        }
                    }
                },
                "400": {
                    "description": "Error en la solicitud (parámetros faltantes o inválidos)",
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
                                        "example": "El parámetro 'category_id' es requerido"
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
            "parameters": [
                {
                    "name": "body",
                    "in": "body",
                    "description": "ID de la categoría",
                    "required": True,
                    "schema": {
                        "type": "object",
                        "required": ["category_id"],
                        "properties": {
                            "category_id": {
                                "type": "integer",
                                "description": "ID de la categoría de unidades de medida",
                                "example": 35
                            }
                        }
                    }
                }
            ],
            "security": [{"public": []}]
        }

    @http.route(
        "/api_serena/v1/list_all_uom",
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
    )
    def get_list_all_uom(self, **kwargs):
        try:
            data = (
                request.env["uom.uom"]
                .sudo()
                .search_read(
                    [('is_uom_sc','=',True)],
                    ["id", "name","category"],
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

    @http.route(
        "/api_serena/v1/list_uom_this_category",
        type="json",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def get_list_uom_this_category(self, **kwargs):
        try:
            parameters = [
                "category_id",
            ]
            data = self._get_json_data(request.httprequest.data)
            self._check_existence_parameters(parameters, data)
            
            current_db = request.env.cr.dbname
            category_id = data["category_id"]

            answer = {}
            # Usar Registry directamente como recomienda el warning
            registry = Registry(current_db)

            with registry.cursor() as cr:
                env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
                UoMUoM = env["uom.uom"].sudo()
                answer = UoMUoM.search_read(
                    [('is_uom_sc','=',True),('category_id','=',category_id)],
                    ["id", "name","category"],
                )                
            answer = {
                    "status": "success",
                    "message": "Registro creado exitosamente",
                    "data": answer,
                }
            _logger.info(f"Response: {answer}")
            return Response(
                answer,
                headers={"Content-Type": "application/json"},
            )
        except Exception as e:
            return self._handle_error(e)