import json
import math

from odoo import _, http
from odoo.http import Response, request

from ..controllers_base import BaseAPIController


class ScaleGDS5QuestionAPIController(BaseAPIController):
    
    def doc_get_list_gds5_question(self):
        """
        Documentación Swagger para el método get_list_scalegds5_question
        
        Returns:
            dict: Documentación Swagger para el endpoint de listado de preguntas asociada a la evaluación geriatrica GDS-5
        """
        return {
            "tags": ["Evaluación Geriatrica - GDS-5"],
            "summary": "Lista las preguntas asociada a la evaluación geriatrica GDS-5",
            "description": (
                "Retorna un listado de todas las preguntas activas para realizar la evaluación geriatrica GDS-5. "
                "Cada pregunta incluye información sobre su puntuación y la respuesta que indica posible depresión. "
                "Usado en el proceso de evaluación psicológica y seguimiento del bienestar emocional."
            ),
            "responses": {
                "200": {
                    "description": "Listado de preguntas asociada a la evaluación geriatrica GDS-5",
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
                                                "statement": {
                                                    "type": "string",
                                                    "description": "Enunciado completo de la pregunta",
                                                    "example": "¿Está satisfecho con su vida?"
                                                },
                                                "point_value": {
                                                    "type": "integer",
                                                    "description": "Valor en puntos que representa la pregunta",
                                                    "example": 1
                                                },
                                                "depression_answer": {
                                                    "type": "string",
                                                    "description": "Respuesta que indica posible depresión ('0' para no, '1' para sí)",
                                                    "example": "1"
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
        "/api_serena/v1/list_gds5_question",
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
    )
    def get_list_gds5_question(self, **kwargs):
        try:
            data = (
                request.env["scalegds5.question"]
                .sudo()
                .search_read(
                    [('active', '=', True)],
                    ["id", "name", "statement", "point_value", "depression_answer"],
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