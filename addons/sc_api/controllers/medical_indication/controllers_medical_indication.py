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

class MedicalIndicationController(BaseAPIController):


    @http.route(
        "/api_serena/v1/list_medical_indication_this_resident",
        type='json', 
        auth="none", 
        methods=['POST'], 
        csrf=False
    )
    def list_medical_indication_this_resident(self, **post):
        try:
            parameters = [
                'resident_id',
                'type_indication',
            ]
            token = self._get_token()
            payload = self._get_payload(token)
            data = self._get_json_data(request.httprequest.data)
            self._check_existence_parameters(parameters, data)
            
            current_db = request.env.cr.dbname
            user_id = payload['user_id']
            residence_id = payload['residence_id']
            resident_id = data['resident_id']
            type_indication = data['type_indication']

            type_vs_model_indication = {
                'all':'unified.medical.indication',
                'general':'medical.indication',
                'medication':'medical.medication',
            }

            model_indication = type_vs_model_indication.get(type_indication,None)

            if not model_indication:
               raise Exception("El tipo de indicación médica aún no está implementada "
                               "por el sistema actualmente")

            answer = {}
            data = []
            # Usar Registry directamente como recomienda el warning
            registry = Registry(current_db)
            with registry.cursor() as cr:
                env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
                ModelIndication = env[model_indication].sudo()
                ResUsers = env['res.users'].sudo()
                Resident = env['resident'].sudo()
                resident = None 
                user = None 
                # - Chequear que usuario tenga sessión activa
                user = ResUsers.browse(user_id)
            
                if not user:
                    raise AccessDenied("Usuario no encontrado")
                
                if not user.jwt_token or not user.token_expiration:
                    raise AccessDenied("El usuario no tiene sessión iniciada")

                # - Chequar que el usuario tenga los permisos para hacer
                # la lectura de las indicaciones medica TODO

                # - Chequear que exista el residente
                resident = Resident.browse(resident_id)

                if not resident:
                   raise AccessDenied("Residente no encontrado")
                
                # - Chequear que en la residencia donde trabaja el usuario
                # en esta sessión sea la misma que la del residente
                if resident and resident.residence_id.id != residence_id:
                   raise AccessDenied("El residente no se encuentra en la residencia en el que\
 usuario se autentico") 
                # Obtener las indicaciones médicas del residente ordenadas descendentemente
                # por la fecha de elaboración.
                list_fields = ["id", "create_date", "resident_data", "user_data", "note"]

                if model_indication == 'medical.medication':
                    list_fields = list_fields + [
                                                    "medicament_data",
                                                    "pharmaceutical_form_data",
                                                    "route_data",
                                                    "dosage_amount",
                                                    "dosage_unit_data",
                                                    "frequency_amount",
                                                    "frequency_unit_data",
                                                    "start_date_medication",
                                                    "end_date_medication",
                                                ]
                
                data = ModelIndication.search_read(
                            domain=[("resident_id","=",resident_id)],
                            fields=list_fields,
                            order="create_date desc"
                        )
                fields_date =["create_date", "start_date_medication", "end_date_medication"]
                for d in data:
                    for f in fields_date:
                        if d and f in d and d[f]:
                            d[f] = self._convert_to_iso(d[f])
            answer = json.dumps({
                        "status": "success", 
                        "message": "Datos obtenidos satifactoriamente",  
                        "data": data
                    })     
            _logger.info(f"Response: {answer}")
 
            return Response( answer,headers={"Content-Type": "application/json"}, )
        except Exception as e:
            return self._handle_error(e)