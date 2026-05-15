import json
import math

from odoo import _, http
from odoo.http import Response, request

from ..controllers_base import BaseAPIController


class BarthelQuestionAPIController(BaseAPIController):

    def doc_get_list_barthel_question(self):
        """
        Documentación Swagger para el método get_list_barthel_question

        Returns:
            dict: Documentación Swagger para el endpoint de listado de preguntas asociada a la evaluación geriatrica Barthel
        """
        return {
            "tags": ["Evaluación Geriatrica - Barthel"],
            "summary": "Lista las preguntas asociada a la evaluación geriatrica Barthel",
            "description": (
                "Retorna un listado de todas las preguntas activas para realizar la evaluación geriatrica Barthel. "
                "Cada pregunta incluye información sobre ella y sus posibles "
                "respuestas "
                "Usado en el proceso de evaluación psicológica y seguimiento del bienestar emocional."
            ),
            "responses": {
                "200": {
                    "description": "Listado de preguntas asociada a la evaluación geriatrica Barthel",
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
                                        "description": "Arreglo de objetos con información de preguntas de estado de ánimo",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "id": {
                                                    "type": "integer",
                                                    "description": "ID único de la pregunta",
                                                    "example": 1
                                                },
                                                "name": {
                                                    "type": "string",
                                                    "description": "Nombre identificador de la pregunta",
                                                    "example": "Pregunta 1"
                                                },
                                                "order": {
                                                    "type": "integer",
                                                    "description": "Orden o "
                                                                   "posición "
                                                                   "que ocupa la pregunta en la "
                                                                   "secuencia de las diferentes preguntas",
                                                    "example": 2
                                                },
                                                "choises":{
                                                    "type": "array",
                                                    "description": "Arreglo con las posibles respuestas que puede tener la pregunta",
                                                    "items": {
                                                        "type": "object",
                                                        "properties": {
                                                            "id": {
                                                                "type": "integer",
                                                                "description": "Identificador de la opción de respuesta",
                                                                "example": 5
                                                            },
                                                            "name": {
                                                                "type": "string",
                                                                "description": "Nombre de la opción de respuesta",
                                                                "example": "Niguna"
                                                            },
                                                            "value": {
                                                                "type": "float",
                                                                "description": "Puntuación que se otorga si selecciona esta opción como respuesta",
                                                                "example": 2.0
                                                            }
                                                        }
                                                    }
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
        "/api_serena/v1/list_barthel_question",
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
    )
    def get_list_barthel_question(self, **kwargs):
        try:
            data = (
                request.env["barthel.question"]
                .sudo()
                .search_read(
                    domain = [('active', '=', True)],
                    fields = [
                        "id",
                        "name",
                        "order",
                        "choises",
                    ],
                    order="order"
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
