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

class ResidentController(BaseAPIController):

    @http.route(
        "/api_serena/v1/list_residents_this_residence",
        type='json', 
        auth="none", 
        methods=['POST'], 
        csrf=False
    )
    def list_residents_this_residence(self, **post):
        try:
            # Extraer token del encabezado Authorization
            auth_header = http.request.httprequest.headers.get('Authorization')
            if not auth_header or 'Bearer ' not in auth_header:
                raise Exception("Encabezado de autorización inválido")
            
            token = auth_header.split('Bearer ')[1].strip()
        
            # Obtener base de datos directamente del entorno actual
            current_db = request.env.cr.dbname
        
            answer = []
            # Usar Registry directamente como recomienda el warning
            registry = Registry(current_db)
            with registry.cursor() as cr:
                env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
                payload = jwt.decode(token, BaseAPIController.SECRET_KEY, algorithms=[BaseAPIController.ALGORITHM])
                user_id = payload['user_id']
                residence_id = payload['residence_id']
            
                # Buscar usuario en la base de datos actual
                users = env['res.users'].sudo().search([
                    ("id", "=", user_id),
                    ("jwt_token", "=", token)
                ])
            
                if users:
                    # Obtener residentes usando el mismo entorno
                    data = env["resident"].sudo().search_read(
                        [("residence_id", "=", residence_id)],
                        ["id", "name", "image_1920"]
                    )
                
                    for d in data:
                        if d.get("image_1920"):
                            d["image_1920"] = base64.b64encode(d["image_1920"]).decode("utf-8")
                    answer = data
                else:
                    raise Exception("Usuario no autenticado")
                
            _logger.info(f"Response: {answer}")
 
            return Response(
                json.dumps({"status": "success", "data": answer}),
                headers={"Content-Type": "application/json"},
            )
        except Exception as e:
            return self._handle_error(e)