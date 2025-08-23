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

    @http.route(
        "/api_serena/v1/list_all_uom",
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
    )
    def get_list_all_uom(self, **kwargs):
        """
        Obtiene todas las unidades de medida gestionadas por Serena-Care
        
        ---
        tags:
          - Unidades de Medida
        summary: Obtener todas las unidades de medida
        description: |
          Este endpoint retorna todas las unidades de medida que están marcadas
          como gestionadas por Serena-Care (is_uom_sc=True).
          
          Incluye información básica como ID, nombre y categoría.
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
            description: Lista de unidades de medida obtenida exitosamente
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
                            description: ID único de la unidad de medida
                            example: 1
                          name:
                            type: string
                            description: Nombre de la unidad de medida
                            example: Gramo
                          category:
                            type: array
                            description: Información de la categoría (puede variar según estructura de Odoo)
                            items:
                              type: object
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
            return self._handle_error(e)

    @http.route(
        "/api_serena/v1/list_uom_this_category",
        type="json",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def get_list_uom_this_category(self, **kwargs):
        """
        Obtiene las unidades de medida de una categoría específica gestionadas por Serena-Care
        
        ---
        tags:
          - Unidades de Medida
        summary: Obtener unidades de medida por categoría
        description: |
          Este endpoint retorna las unidades de medida de una categoría específica
          que están marcadas como gestionadas por Serena-Care (is_uom_sc=True).
          
          Requiere el ID de la categoría en el cuerpo de la solicitud.
        parameters:
          - name: Authorization
            in: header
            description: Token de autenticación (si es requerido)
            required: false
            schema:
              type: string
            example: Bearer your-token-here
          - name: body
            in: body
            description: ID de la categoría
            required: true
            schema:
              type: object
              required:
                - category_id
              properties:
                category_id:
                  type: integer
                  description: ID de la categoría de unidades de medida
                  example: 1
        responses:
          200:
            description: Lista de unidades de medida obtenida exitosamente
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
                      example: Registro creado exitosamente
                    data:
                      type: array
                      items:
                        type: object
                        properties:
                          id:
                            type: integer
                            description: ID único de la unidad de medida
                            example: 1
                          name:
                            type: string
                            description: Nombre de la unidad de medida
                            example: Gramo
                          category:
                            type: array
                            description: Información de la categoría (puede variar según estructura de Odoo)
                            items:
                              type: object
          400:
            description: Error en la solicitud (parámetros faltantes o inválidos)
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
                      example: El parámetro 'category_id' es requerido
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
             
            answer = json.dumps(
                {
                    "status": "success",
                    "message": "Registro creado exitosamente",
                    "data": answer,
                }
            )
            _logger.info(f"Response: {answer}")

            return Response(
                answer,
                headers={"Content-Type": "application/json"},
            )
        except Exception as e:
            return self._handle_error(e)