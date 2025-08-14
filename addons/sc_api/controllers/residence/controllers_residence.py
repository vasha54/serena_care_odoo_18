import json
import math

from odoo import _, http
from odoo.http import Response, request

from ..controllers_base import BaseAPIController


class ResidenceAPIController(BaseAPIController):

    @http.route(
        "/api_serena/v1/list_residence_login",
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
    )
    def get_list_residence_login(self, **kwargs):
        """
        Obtiene el listado de residencias disponibles para login
        ---
        tags:
          - Residences
        summary: Lista de residencias para selección en login
        description: |
          Retorna un listado de todas las residencias disponibles en el sistema
          con su ID y nombre. Usado en el proceso de login para que los usuarios
          seleccionen su residencia.
        responses:
          200:
            description: Listado de residencias obtenido exitosamente
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    status:
                      type: string
                      example: success
                    message:
                      type: string
                      example: "Datos obtenidos correctamente"
                    data:
                      type: array
                      items:
                        type: object
                        properties:
                          id:
                            type: integer
                            description: ID único de la residencia
                            example: 1
                          name:
                            type: string
                            description: Nombre de la residencia
                            example: "Residencia Principal"
          400:
            description: Parámetros inválidos en la solicitud
          500:
            description: Error interno del servidor
        """
        try:
            data = (
                request.env["residence_house"]
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
            return self._handle_error(e)