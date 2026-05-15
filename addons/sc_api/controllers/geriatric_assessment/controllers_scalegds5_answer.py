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


class ScaleGDS5AnswerAPIController(BaseAPIController):
    
    def doc_register_gds5_answers(self):
        """
        Documentación Swagger para el método register_gds5_answers
        
        Returns:
            dict: Documentación Swagger para el endpoint de registrar respuestas de evaluación de GDS-5
        """
        return {
            "tags": ["Evaluación Geriatrica - GDS-5"],
            "summary": "Registrar respuestas de evaluación de GDS-5 para un residente",
            "description": """
            Endpoint para registrar una evaluación completa de GDS-5 de un residente,
            incluyendo todas las respuestas a las preguntas del cuestionario. Requiere autenticación JWT válida.

            **Cabeceras requeridas:**
            - Content-Type: application/json
            - Authorization: Bearer <token_jwt>

            **Proceso:**
            1. Valida la sesión del usuario y los permisos
            2. Verifica que el residente pertenezca a la residencia del usuario
            3. Valida que todas las preguntas existan y estén activas
            4. Crea una evaluación de GDS-5
            5. Registra todas las respuestas individuales
            6. Asocia las respuestas a la evaluación
            """,
            "parameters": [
                {
                    "name": "Authorization",
                    "in": "header",
                    "required": True,
                    "description": "Token JWT de autenticación en formato 'Bearer {token}'",
                    "schema": {
                        "type": "string"
                    },
                    "example": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
                },
                {
                    "name": "Content-Type",
                    "in": "header",
                    "required": True,
                    "description": "Tipo de contenido debe ser application/json",
                    "schema": {
                        "type": "string",
                        "enum": ["application/json"]
                    },
                    "example": "application/json"
                },
                {
                    "name": "body",
                    "in": "body",
                    "required": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "resident_id": {
                                "type": "integer",
                                "description": "Identificador del residente al cual se le aplica la evaluación de GDS-5",
                                "example": 4
                            },
                            "clinic_note": {
                                "type": "string",
                                "description": "Cadena de texto o vacía que contiene alguna observación reerente al residente cuando se le aplica la evaluación de GDS-5",
                                "example": "Nota de observación durante la evaluación"
                            },
                            "date": {
                                "type": "string",
                                "format": "date-time",
                                "description": "Fecha y hora que se hace la anotación en formato '%Y-%m-%d %H:%M:%S'",
                                "example": "2025-08-20 10:00:00",
                            },
                            "answers": {
                                "type": "array",
                                "description": "Lista de respuestas a las preguntas del cuestionario de GDS-5",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "question_id": {
                                            "type": "integer",
                                            "description": "Identificador de la pregunta del cuestionario de GDS-5",
                                            "example": 1
                                        },
                                        "answer": {
                                            "type": "integer",
                                            "description": "Valor de la respuesta (generalmente numérico, 0 si respondio No  y 1 si respondío Sí)",
                                            "example": 0
                                        }
                                    },
                                    "required": ["question_id", "answer"]
                                },
                                "example": [
                                    {"question_id": 1, "answer": 0},
                                    {"question_id": 2, "answer": 0},
                                    {"question_id": 3, "answer": 0},
                                    {"question_id": 4, "answer": 0},
                                    {"question_id": 5, "answer": 0},
                                    {"question_id": 6, "answer": 0},
                                    {"question_id": 7, "answer": 0},
                                    {"question_id": 8, "answer": 0},
                                    {"question_id": 9, "answer": 0},
                                    {"question_id": 10, "answer": 0},
                                    {"question_id": 11, "answer": 1},
                                    {"question_id": 12, "answer": 0},
                                    {"question_id": 13, "answer": 0},
                                    {"question_id": 14, "answer": 1},
                                    {"question_id": 15, "answer": 1}
                                ]
                            }
                        },
                        "required": [
                            "resident_id",
                            "answers",
                            "clinic_note",
                            "date",
                        ]
                    }
                }
            ],
            "responses": {
                "200": {
                    "description": "Evaluación de GDS-5 registrada exitosamente",
                    "headers": {
                        "Content-Type": {
                            "type": "string",
                            "description": "Tipo de contenido de la respuesta"
                        }
                    },
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "status": {
                                        "type": "string",
                                        "example": "success"
                                    },
                                    "message": {
                                        "type": "string",
                                        "example": "Registro creado existosamente"
                                    },
                                    "data": {
                                        "type": "object",
                                        "properties": {
                                            "id": {
                                                "type": "integer",
                                                "description": "Identificador de la evaluación de GDS-5 creada",
                                                "example": 6
                                            },
                                            "date": {
                                                "type": "string",
                                                "format": "date-time",
                                                "description": "Fecha y hora de creación de la evaluación en formato ISO",
                                                "example": "2025-10-11T15:30:00Z"
                                            },
                                            "user_id": {
                                                "type": "integer",
                                                "description": "Identificador del usuario que realizó la evaluación",
                                                "example": 10
                                            },
                                            "user_name": {
                                                "type": "string",
                                                "description": "Nombre del usuario que realizó la evaluación",
                                                "example": "Dr. Carlos Ruiz"
                                            },
                                            "resident_id": {
                                                "type": "integer",
                                                "description": "Identificador del residente evaluado",
                                                "example": 4
                                            },
                                            "resident_name": {
                                                "type": "string",
                                                "description": "Nombre del residente evaluado",
                                                "example": "Ana Flores Ramírez"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "400": {
                    "description": "Parámetros faltantes, inválidos o estructura incorrecta de respuestas",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "example": "error"
                            },
                            "message": {
                                "type": "string",
                                "example": "Faltan parámetros requeridos o la estructura de respuestas es incorrecta"
                            },
                            "data": {
                                "type": "null",
                                "example": None
                            }
                        }
                    }
                },
                "401": {
                    "description": "Token inválido o sesión no iniciada",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "example": "error"
                            },
                            "message": {
                                "type": "string",
                                "example": "El usuario no tiene sessión iniciada"
                            },
                            "data": {
                                "type": "null",
                                "example": None
                            }
                        }
                    }
                },
                "403": {
                    "description": "Acceso denegado - Residente no pertenece a la residencia del usuario",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "example": "error"
                            },
                            "message": {
                                "type": "string",
                                "example": "El residente no se encuentra en la residencia en el que usuario se autentico"
                            },
                            "data": {
                                "type": "null",
                                "example": None
                            }
                        }
                    }
                },
                "404": {
                    "description": "Residente no encontrado o pregunta de GDS-5 no existe",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "example": "error"
                            },
                            "message": {
                                "type": "string",
                                "example": "Residente no encontrado o pregunta de GDS-5 no existe en el sistema"
                            },
                            "data": {
                                "type": "null",
                                "example": None
                            }
                        }
                    }
                },
                "500": {
                    "description": "Error interno del servidor",
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
            },
            "security": [
                {
                    "bearerAuth": []
                }
            ]
        }
    
    
    @http.route(
        "/api_serena/v1/register_gds5_answers",
        type="json",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def register_gds5_answers(self, **kwargs):
        try:
            parameters = [
                'resident_id',
                'answers',
                'clinic_note',
                'date',
            ]
            token = self._get_token()
            payload = self._get_payload(token)
            data = self._get_json_data(request.httprequest.data)
            self._check_existence_parameters(parameters, data)
            
            current_db = request.env.cr.dbname
            user_id = payload['user_id']
            residence_id = payload['residence_id']
            resident_id = data['resident_id']
            gds5_answers = data['answers']
            clinic_note = data['clinic_note']
            
            answer = {}
            # Usar Registry directamente como recomienda el warning
            registry = Registry(current_db)
            with registry.cursor() as cr:
                env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
                ScaleGDS5Answer = env['scalegds5.answer'].sudo()
                ScaleGDS5Question = env['scalegds5.question'].sudo()
                ScaleGDS5Assessment = env['scalegds5.assessment'].sudo()
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
                if not self._check_user_permissions(user, 'scalegds5.answer', self.CAN_CREATE, env):
                    raise AccessDenied("El usuario no tiene los permisos para esta operación")
                if not self._check_user_permissions(user, 'scalegds5.assessment', self.CAN_CREATE, env):
                    raise AccessDenied("El usuario no tiene los permisos para esta operación")

                # - Chequear que exista el residente 
                resident = Resident.browse(resident_id)

                if not resident:
                   raise AccessDenied("Residente no encontrado")
                
                # - Chequear que en la residencia donde trabaja el usuario
                # en esta sessión sea la misma que la del residente
                if resident and resident.residence_id.id != residence_id:
                   raise AccessDenied("El residente no se encuentra en la residencia en el que\
 usuario se autentico")

                # - Chequear que todas pregunts utilizadas en la evaluacion estén activas y con los campos requeridos
                for index, obj in enumerate(gds5_answers):
                    # Validar que cada elemento sea un diccionario (objeto)
                    if not isinstance(obj, dict):
                        raise Exception( f'La respuesta en la posicion {index} no es un objeto valido: {obj}' )
                
                    # Validar la presencia de las dos propiedades esperadas
                    if not 'question_id' in obj or not 'answer' in obj:
                        raise Exception( f'El objeto en la posicion {index} no tiene las propiedades requeridas. Se esperan "question_id" y "answer". object_received : {obj}')
                
                    # Extraer los valores para su uso
                    question_id = obj['question_id']
                    answer = str(obj['answer'])
                   
                    question = ScaleGDS5Question.browse(question_id)
                    
                    if not question:
                        raise Exception("No existe una pregunta de GDS-5 en el sistema con ese identificador")
                    if not question.active:
                        raise Exception("La pregunta de estado de GDS-5 no se encuentra activa ")

                date_adjust = self._adjust_timezone(user, data['date'])
                # - Crear evaluacion
                assessment = ScaleGDS5Assessment.create({
                    'resident_id': resident.id,
                    'user_id':user.id,
                    'clinic_note':clinic_note,
                    'date': date_adjust ,
                })

                # - Registrar respuestas
                answers_id = []
                for index, obj in enumerate(gds5_answers):
                    question_id = obj['question_id']
                    answer_str = str(obj['answer'])
                    obj = ScaleGDS5Answer.create({
                            'resident_id': resident.id,
                            'user_id': user.id,
                            'assessment_id': assessment.id,
                            'question_id': question_id,
                            'answer_select': answer_str,
                        })
                    answers_id.append(obj.id)

                # - Asociar las respuestas a la evaluación 
                assessment.write({'question_answers':[(6,0,answers_id)]})

                if assessment:
                    answer = {
                                "id": assessment.id,
                                "date": self._convert_to_iso(assessment.date),
                                "user_id": assessment.user_id.id,
                                "user_name": assessment.user_id.name,
                                "resident_id": assessment.resident_id.id,
                                "resident_name": assessment.resident_id.name,
                            }
           
            answer = {
                        "status": "success", 
                        "message": "Registro creado existosamente",  
                        "data": answer
                    }     
            return answer
        except Exception as e:
            return self._handle_error(e)