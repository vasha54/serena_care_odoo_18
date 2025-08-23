import yaml
import re
import logging
import json
from odoo import http
from odoo.http import Response, request

from .uom import controllers_category_uom as ccuom, controllers_oum as cuom

_logger = logging.getLogger(__name__)

class APIDocsController(http.Controller):
    
    @http.route('/api-docs', type='http', auth="public", methods=['GET'])
    def get_api_docs(self, **kwargs):
        """
        Endpoint para documentación Swagger/OpenAPI
        ---
        tags:
          - Documentation
        summary: Obtener documentación de la API en formato OpenAPI
        description: Retorna la especificación OpenAPI de todos los endpoints disponibles
        responses:
          200:
            description: Documentación OpenAPI
            content:
              application/json:
                schema:
                  type: object
        """
        # Recopilar todos los endpoints documentados
        docs = {
            "openapi": "3.0.0",
            "info": {
                "title": "API Serena",
                "version": "1.0.0",
                "description": "API para gestión de unidades de medida y categorías"
            },
            "paths": {
                "/api_serena/v1/list_all_uom": {
                    "get": self.extract_docs(cuom.UoMController.get_list_all_uom)
                },
                "/api_serena/v1/list_uom_this_category": {
                    "post": self.extract_docs(cuom.UoMController.get_list_uom_this_category)
                },
                "/api_serena/v1/list_category_uom": {
                    "get": self.extract_docs(ccuom.CategoryUoMController.get_list_category_uom)
                }
                # Agregar más endpoints aquí según sea necesario
            },
            "components": {
                "securitySchemes": {
                    "bearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    }
                }
            }
        }
        
        return Response(
            json.dumps(docs), 
            headers={"Content-Type": "application/json"}
        )
    
    def extract_docs(self, method):
        """
        Extrae la documentación OpenAPI del docstring de un método
        
        Args:
            method: El método del controlador con documentación OpenAPI en su docstring
            
        Returns:
            dict: Diccionario con la documentación OpenAPI parseada
        """
        if not method or not method.__doc__:
            _logger.warning(f"Método o docstring no encontrado para: {method}")
            return {}
        
        docstring = method.__doc__
        
        # Buscar el contenido YAML dentro del docstring
        yaml_content = self._extract_yaml_from_docstring(docstring)
        
        if not yaml_content:
            _logger.warning(f"No se encontró contenido YAML en el docstring de: {method.__name__}")
            return {}
        
        try:
            # Parsear el YAML a un diccionario de Python
            parsed_docs = yaml.safe_load(yaml_content)
            return parsed_docs
        except yaml.YAMLError as e:
            _logger.error(f"Error al parsear YAML del método {method.__name__}: {e}")
            return {}
    
    def _extract_yaml_from_docstring(self, docstring):
        """
        Extrae el contenido YAML de un docstring que contiene documentación OpenAPI
        
        Args:
            docstring (str): El docstring completo del método
            
        Returns:
            str: El contenido YAML extraído, o None si no se encuentra
        """
        # Patrón para encontrar el bloque YAML (entre --- y el final o otro ---)
        pattern = r'^-{3}\s*\n(.*?)(?=^-{3}|\Z)'
        match = re.search(pattern, docstring, re.DOTALL | re.MULTILINE)
        
        if match:
            return match.group(1).strip()
        
        # Si no encuentra el patrón ---, buscar cualquier contenido YAML-like
        lines = docstring.split('\n')
        yaml_lines = []
        in_yaml_block = False
        
        for line in lines:
            # Buscar líneas que parezcan YAML (con indentación y :)
            if re.match(r'^\s*[a-zA-Z]+:', line) or in_yaml_block:
                in_yaml_block = True
                yaml_lines.append(line)
            # Detener si encontramos una línea que no es YAML y estábamos en un bloque
            elif in_yaml_block and line.strip() and not re.match(r'^\s', line):
                break
        
        if yaml_lines:
            return '\n'.join(yaml_lines)
        
        return None

