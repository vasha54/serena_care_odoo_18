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

class VitalSignalController(BaseAPIController):

    @http.route(
        "/api_serena/v1/register_vital_signs",
        type='json', 
        auth="none", 
        methods=['POST'], 
        csrf=False
    )
    def regiter_vital_signs(self, **post):
        """
            Registra los signos vitales de un residente
            ---
            tags:
            - Vital Signs
            summary: Registra los signos vitales de un residente
            description: |
            Registra los signos vitales de un residente específico.
            Requiere autenticación JWT válida en el header.
            security:
            - bearerAuth: []
            requestBody:
            required: true
            description: Datos de los signos vitales
            content:
                application/json:
                schema:
                    type: object
                    required:
                    - resident_id
                    - temperature
                    - heart_rate
                    - systolic
                    - diastolic
                    - respiratory_rate
                    - weight
                    - oxygen_saturation
                    - glucose
                    - grip_strength
                    properties:
                    resident_id:
                        type: integer
                        description: ID del residente
                        example: 12345
                    temperature:
                        type: number
                        format: float
                        description: Temperatura en °C
                        example: 36.5
                    heart_rate:
                        type: integer
                        description: Ritmo cardíaco (ppm)
                        example: 75
                    systolic:
                        type: integer
                        description: Presión arterial sistólica (mmHg)
                        example: 120
                    diastolic:
                        type: integer
                        description: Presión arterial diastólica (mmHg)
                        example: 80
                    respiratory_rate:
                        type: integer
                        description: Frecuencia respiratoria (rpm)
                        example: 16
                    weight:
                        type: number
                        format: float
                        description: Peso en kg
                        example: 68.5
                    oxygen_saturation:
                        type: number
                        format: float
                        description: Saturación de oxígeno (%)
                        example: 98.0
                    glucose:
                        type: number
                        format: float
                        description: Nivel de glucosa (mg/dL)
                        example: 95.0
                    grip_strength:
                        type: integer
                        description: Fuerza de agarre (kg)
                        example: 32
            responses:
            200:
                description: Registro exitoso
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
                        example: Registro creado existosamente
                        data:
                        type: object
                        properties:
                            id:
                            type: integer
                            example: 987
                            date:
                            type: string
                            format: date-time
                            example: "2025-08-18T14:30:00Z"
                            user_id:
                            type: integer
                            example: 543
                            user_name:
                            type: string
                            example: "Enfermero Principal"
                            resident_id:
                            type: integer
                            example: 12345
                            resident_name:
                            type: string
                            example: "María González"
            400:
                description: Parámetros faltantes o inválidos
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
                        example: "Faltan parámetros requeridos: temperature, heart_rate"
                        data:
                        type: null
                        example: null
            401:
                description: Token inválido o sesión no iniciada
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
                        example: "El usuario no tiene sessión iniciada"
                        data:
                        type: null
                        example: null
            403:
                description: Acceso denegado
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
                        example: "El residente no se encuentra en la residencia del usuario"
                        data:
                        type: null
                        example: null
            404:
                description: Residente no encontrado
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
                        example: "Residente no encontrado"
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
                        example: "Error interno del servidor"
                        data:
                        type: null
                        example: null
        """
        try:
            parameters = [
                'resident_id',
                'temperature',
                'heart_rate',
                'systolic',
                'diastolic',
                'respiratory_rate',
                'weight',
                'oxygen_saturation',
                'glucose',
                'grip_strength'
            ]
            token = self._get_token()
            payload = self._get_payload(token)
            data = self._get_json_data(request.httprequest.data)
            self._check_existence_parameters(parameters, data)
            
            current_db = request.env.cr.dbname
            user_id = payload['user_id']
            residence_id = payload['residence_id']
            resident_id = data['resident_id']

            answer = {}
            # Usar Registry directamente como recomienda el warning
            registry = Registry(current_db)

            with registry.cursor() as cr:
                env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
                VitalSigns = env['vital.signs'].sudo()
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
                # el registro TODO
                # - Chequear que exista el residente 
                resident = Resident.browse(resident_id)

                if not resident:
                   raise AccessDenied("Residente no encontrado")
                
                # - Chequear que en la residencia donde trabaja el usuario
                # en esta sessión sea la misma que la del residente
                if resident and resident.residence_id.id != residence_id:
                   raise AccessDenied("El residente no se encuentra en la residencia en el que\
 usuario se autentico") 
                
                # Registrar la medición del signo vital
                record_vs = VitalSigns.create({
                                'resident_id': resident.id,
                                'user_id':user.id,
                                'temperature':data['temperature'],
                                'heart_rate':data['heart_rate'],
                                'systolic':data['systolic'],
                                'diastolic':data['diastolic'],
                                'respiratory_rate':data['respiratory_rate'],
                                'weight':data['weight'],
                                'oxygen_saturation':data['oxygen_saturation'],
                                'glucose':data['glucose'],
                                'grip_strength':data['grip_strength'],
                            })
                if record_vs:
                    answer = {
                                "id": record_vs.id,
                                "date": self._convert_to_iso(record_vs.date),
                                "user_id": record_vs.user_id.id,
                                "user_name": record_vs.user_id.name,
                                "resident_id": record_vs.resident_id.id,
                                "resident_name": record_vs.resident_id.name,
                            }     

            answer = json.dumps({
                        "status": "success", 
                        "message": "Registro creado existosamente",  
                        "data": answer
                    })     
            _logger.info(f"Response: {answer}")
 
            return Response( answer,headers={"Content-Type": "application/json"}, )
            
        except Exception as e:
            return self._handle_error(e)
