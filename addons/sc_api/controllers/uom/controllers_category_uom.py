import json
import math

from odoo import _, http
from odoo.http import Response, request

from ..controllers_base import BaseAPIController


class CategoryUoMController(BaseAPIController):

    @http.route(
        "/api_serena/v1/list_category_uom",
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
    )
    def get_list_category_uom(self, **kwargs):
        """
        Obtiene la lista de categorías de unidades de medida gestionadas por Serena-Care
        
        ---
        tags:
          - Unidades de Medida
        summary: Obtener categorías de unidades de medida
        description: |
          Este endpoint retorna todas las categorías de unidades de medida 
          que están marcadas como gestionadas por Serena-Care (is_uom_sc=True).
          
          Las categorías incluyen información básica como ID y nombre.
        parameters:
          - name: Authorization
            in: header
            description: Token de autenticación (si es requerido)
            required: false
            schema:
              type: string
            example: Bearer your-token-here
        responses:
          200:
            description: Lista de categorías obtenida exitosamente
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
                      example: Datos obtenidos correctamente
                    data:
                      type: array
                      items:
                        type: object
                        properties:
                          id:
                            type: integer
                            description: ID único de la categoría
                            example: 1
                          name:
                            type: string
                            description: Nombre de la categoría
                            example: Peso
          400:
            description: Error en la solicitud
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    status:
                      type: string
                      example: error
                    message:
                      type: string
                      example: Descripción del error
                    data:
                      type: null
                      example: null
          500:
            description: Error interno del servidor
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    status:
                      type: string
                      example: error
                    message:
                      type: string
                      example: Error interno del servidor
                    data:
                      type: null
                      example: null
        security:
          - bearerAuth: []
        """
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
            return self._handle_error(e)