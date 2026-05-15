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

class MedicalResidentStateAPIController(BaseAPIController):
    
    def doc_get_general_condition_residents_of_residence(self):
        """
        Documentación Swagger para el método get_general_condition_residents_of_residence

        Returns:
            dict: Documentación Swagger para el endpoint de obtener estado general de residentes
        """
        return {
            "tags": ["Residentes"],
            "summary": "Obtener el estado general de todos los residentes de una residencia",
            "description": """
            Endpoint para obtener el último estado general registrado de cada residente
            en la residencia donde el usuario está autenticado. 
            
            **Características principales:**
            - Devuelve un resumen por estado (Desconocido, Crítico, En Observación, Estable)
            - Para cada residente, incluye el último estado general registrado
            - Proporciona detalles completos de las 4 evaluaciones que componen el estado general:
            1. **Evaluación de Anomalía**: Estado basado en anomalías registradas
            2. **Escala de Dolor**: Estado basado en evaluación del dolor
            3. **Evaluación Neurológica**: Estado basado en evaluación neurológica
            4. **Signos Vitales**: Estado basado en múltiples parámetros vitales (temperatura, frecuencia cardíaca, etc.)
            
            **Estructura de la respuesta:**
            - `status_summary`: Resumen estadístico por estado (conteo y porcentaje)
            - `states`: Lista detallada por cada residente con todas las evaluaciones
            
            **Cabeceras requeridas:**
            - Content-Type: application/json
            - Authorization: Bearer <token_jwt>
            """,
            "parameters": [
                {
                    "name": "Authorization",
                    "in": "header",
                    "required": True,
                    "description": "Token JWT de autenticación en formato 'Bearer {token}'",
                    "schema": {"type": "string"},
                    "example": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                },
                {
                    "name": "Content-Type",
                    "in": "header",
                    "required": True,
                    "description": "Tipo de contenido debe ser application/json",
                    "schema": {"type": "string", "enum": ["application/json"]},
                    "example": "application/json",
                }
            ],
            "responses": {
                "200": {
                    "description": "Datos del estado general obtenidos exitosamente",
                    "headers": {
                        "Content-Type": {
                            "type": "string",
                            "description": "Tipo de contenido de la respuesta",
                        }
                    },
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "status": {
                                        "type": "string",
                                        "description": "Estado de la operación",
                                        "example": "success"
                                    },
                                    "message": {
                                        "type": "string",
                                        "description": "Mensaje descriptivo del resultado",
                                        "example": "Datos obtenidos exitosamente"
                                    },
                                    "data": {
                                        "type": "object",
                                        "description": "Datos principales de la respuesta",
                                        "properties": {
                                            "status_summary": {
                                                "type": "array",
                                                "description": "Resumen estadístico por estado general",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "status_code": {
                                                            "type": "string",
                                                            "description": "Código del estado general",
                                                            "enum": ["-1", "0", "1", "2"],
                                                            "example": "1"
                                                        },
                                                        "label": {
                                                            "type": "string",
                                                            "description": "Etiqueta descriptiva del estado",
                                                            "enum": ["Desconocido", "Crítico", "En Observación", "Estable"],
                                                            "example": "En Observación"
                                                        },
                                                        "count": {
                                                            "type": "integer",
                                                            "description": "Número de residentes con este estado",
                                                            "example": 1
                                                        },
                                                        "percent": {
                                                            "type": "number",
                                                            "format": "float",
                                                            "description": "Porcentaje de residentes con este estado",
                                                            "example": 100.0
                                                        }
                                                    }
                                                }
                                            },
                                            "states": {
                                                "type": "array",
                                                "description": "Lista detallada del estado de cada residente",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "resident": {
                                                            "type": "object",
                                                            "description": "Información del residente",
                                                            "properties": {
                                                                "id": {
                                                                    "type": "integer",
                                                                    "description": "ID del residente",
                                                                    "example": 1
                                                                },
                                                                "name": {
                                                                    "type": "string",
                                                                    "description": "Nombre completo del residente",
                                                                    "example": "Aurora Ines Fajardo Perez"
                                                                }
                                                            }
                                                        },
                                                        "date": {
                                                            "type": "string",
                                                            "format": "date-time",
                                                            "description": "Fecha y hora del registro del estado general",
                                                            "example": "2025-12-31 11:02:06"
                                                        },
                                                        "status": {
                                                            "type": "object",
                                                            "description": "Estado general del residente",
                                                            "properties": {
                                                                "value": {
                                                                    "type": "string",
                                                                    "description": "Código del estado general",
                                                                    "example": "1"
                                                                },
                                                                "label": {
                                                                    "type": "string",
                                                                    "description": "Etiqueta del estado general",
                                                                    "example": "En Observación"
                                                                }
                                                            }
                                                        },
                                                        "anomaly": {
                                                            "type": "object",
                                                            "description": "Evaluación de anomalía del residente",
                                                            "properties": {
                                                                "id": {
                                                                    "type": "integer",
                                                                    "description": "ID del registro de anomalía",
                                                                    "example": 12
                                                                },
                                                                "date": {
                                                                    "type": "string",
                                                                    "format": "date-time",
                                                                    "description": "Fecha y hora de la evaluación de anomalía",
                                                                    "example": "2025-12-29 13:31:00"
                                                                },
                                                                "user": {
                                                                    "type": "object",
                                                                    "description": "Usuario que realizó la evaluación de anomalía",
                                                                    "properties": {
                                                                        "id": {
                                                                            "type": "integer",
                                                                            "description": "ID del usuario",
                                                                            "example": 10
                                                                        },
                                                                        "name": {
                                                                            "type": "string",
                                                                            "description": "Nombre del usuario",
                                                                            "example": "Dr. Carlos Ruiz"
                                                                        }
                                                                    }
                                                                },
                                                                "status": {
                                                                    "type": "object",
                                                                    "description": "Estado resultante de la evaluación de anomalía",
                                                                    "properties": {
                                                                        "value": {
                                                                            "type": "string",
                                                                            "description": "Código del estado",
                                                                            "example": "1"
                                                                        },
                                                                        "label": {
                                                                            "type": "string",
                                                                            "description": "Etiqueta del estado",
                                                                            "example": "En Observación"
                                                                        }
                                                                    }
                                                                },
                                                                "description": {
                                                                    "type": "string",
                                                                    "description": "Descripción detallada de la anomalía",
                                                                    "example": "El residente presenta fiebre persistente por más de 48 horas"
                                                                },
                                                                "anomaly_level": {
                                                                    "type": "object",
                                                                    "description": "Nivel de gravedad de la anomalía",
                                                                    "properties": {
                                                                        "id": {
                                                                            "type": "integer",
                                                                            "description": "ID del nivel de anomalía",
                                                                            "example": 3
                                                                        },
                                                                        "name": {
                                                                            "type": "string",
                                                                            "description": "Nombre del nivel de anomalía",
                                                                            "example": "Moderado"
                                                                        }
                                                                    }
                                                                }
                                                            }
                                                        },
                                                        "pain_scale": {
                                                            "type": "object",
                                                            "description": "Evaluación de escala de dolor del residente",
                                                            "properties": {
                                                                "id": {
                                                                    "type": "integer",
                                                                    "description": "ID del registro de escala de dolor",
                                                                    "example": 1
                                                                },
                                                                "date": {
                                                                    "type": "string",
                                                                    "format": "date-time",
                                                                    "description": "Fecha y hora de la evaluación del dolor",
                                                                    "example": "2025-12-31 11:00:00"
                                                                },
                                                                "user": {
                                                                    "type": "object",
                                                                    "description": "Usuario que realizó la evaluación del dolor",
                                                                    "properties": {
                                                                        "id": {
                                                                            "type": "integer",
                                                                            "description": "ID del usuario",
                                                                            "example": 10
                                                                        },
                                                                        "name": {
                                                                            "type": "string",
                                                                            "description": "Nombre del usuario",
                                                                            "example": "Dr. Carlos Ruiz"
                                                                        }
                                                                    }
                                                                },
                                                                "status": {
                                                                    "type": "object",
                                                                    "description": "Estado resultante de la evaluación del dolor",
                                                                    "properties": {
                                                                        "value": {
                                                                            "type": "string",
                                                                            "description": "Código del estado",
                                                                            "example": "1"
                                                                        },
                                                                        "label": {
                                                                            "type": "string",
                                                                            "description": "Etiqueta del estado",
                                                                            "example": "En Observación"
                                                                        }
                                                                    }
                                                                },
                                                                "description": {
                                                                    "type": "string",
                                                                    "description": "Descripción detallada de la evaluación del dolor",
                                                                    "example": "Dolor moderado en la zona lumbar"
                                                                },
                                                                "value_pain": {
                                                                    "type": "integer",
                                                                    "description": "Valor numérico de la escala de dolor (0-10)",
                                                                    "example": 6
                                                                },
                                                                "pain_status": {
                                                                    "type": "string",
                                                                    "description": "Estado del dolor según la escala",
                                                                    "example": "Dolor moderado"
                                                                }
                                                            }
                                                        },
                                                        "neurological_assessment": {
                                                            "type": "object",
                                                            "description": "Evaluación neurológica del residente",
                                                            "properties": {
                                                                "id": {
                                                                    "type": "integer",
                                                                    "description": "ID del registro de evaluación neurológica",
                                                                    "example": 1
                                                                },
                                                                "date": {
                                                                    "type": "string",
                                                                    "format": "date-time",
                                                                    "description": "Fecha y hora de la evaluación neurológica",
                                                                    "example": "2025-12-31 11:00:00"
                                                                },
                                                                "user": {
                                                                    "type": "object",
                                                                    "description": "Usuario que realizó la evaluación neurológica",
                                                                    "properties": {
                                                                        "id": {
                                                                            "type": "integer",
                                                                            "description": "ID del usuario",
                                                                            "example": 10
                                                                        },
                                                                        "name": {
                                                                            "type": "string",
                                                                            "description": "Nombre del usuario",
                                                                            "example": "Dr. Carlos Ruiz"
                                                                        }
                                                                    }
                                                                },
                                                                "status": {
                                                                    "type": "object",
                                                                    "description": "Estado resultante de la evaluación neurológica",
                                                                    "properties": {
                                                                        "value": {
                                                                            "type": "string",
                                                                            "description": "Código del estado",
                                                                            "example": "1"
                                                                        },
                                                                        "label": {
                                                                            "type": "string",
                                                                            "description": "Etiqueta del estado",
                                                                            "example": "En Observación"
                                                                        }
                                                                    }
                                                                },
                                                                "description": {
                                                                    "type": "string",
                                                                    "description": "Descripción detallada de la evaluación neurológica",
                                                                    "example": "Reflejos normales, coordinación adecuada"
                                                                },
                                                                "neurological_state": {
                                                                    "type": "object",
                                                                    "description": "Estado neurológico específico",
                                                                    "properties": {
                                                                        "id": {
                                                                            "type": "integer",
                                                                            "description": "ID del estado neurológico",
                                                                            "example": 2
                                                                        },
                                                                        "name": {
                                                                            "type": "string",
                                                                            "description": "Nombre del estado neurológico",
                                                                            "example": "Normal"
                                                                        }
                                                                    }
                                                                }
                                                            }
                                                        },
                                                        "vital_signs": {
                                                            "type": "object",
                                                            "description": "Signos vitales del residente y sus estados",
                                                            "properties": {
                                                                "id": {
                                                                    "type": "integer",
                                                                    "description": "ID del registro de signos vitales",
                                                                    "example": 1
                                                                },
                                                                "date": {
                                                                    "type": "string",
                                                                    "format": "date-time",
                                                                    "description": "Fecha y hora de la toma de signos vitales",
                                                                    "example": "2025-12-26 21:39:22"
                                                                },
                                                                "user": {
                                                                    "type": "object",
                                                                    "description": "Usuario que tomó los signos vitales",
                                                                    "properties": {
                                                                        "id": {
                                                                            "type": "integer",
                                                                            "description": "ID del usuario",
                                                                            "example": 10
                                                                        },
                                                                        "name": {
                                                                            "type": "string",
                                                                            "description": "Nombre del usuario",
                                                                            "example": "Dr. Carlos Ruiz"
                                                                        }
                                                                    }
                                                                },
                                                                "temperature": {
                                                                    "type": "number",
                                                                    "format": "float",
                                                                    "description": "Temperatura corporal en grados Celsius",
                                                                    "example": 37.5
                                                                },
                                                                "heart_rate": {
                                                                    "type": "integer",
                                                                    "description": "Frecuencia cardíaca en latidos por minuto",
                                                                    "example": 78
                                                                },
                                                                "glucose": {
                                                                    "type": "number",
                                                                    "format": "float",
                                                                    "description": "Nivel de glucosa en mg/dL",
                                                                    "example": 88.0
                                                                },
                                                                "oxygen_saturation": {
                                                                    "type": "integer",
                                                                    "description": "Saturación de oxígeno en porcentaje",
                                                                    "example": 99
                                                                },
                                                                "blood_pressure": {
                                                                    "type": "string",
                                                                    "description": "Presión arterial en formato sistólica/diastólica",
                                                                    "example": "118/78"
                                                                },
                                                                "respiratory_rate": {
                                                                    "type": "integer",
                                                                    "description": "Frecuencia respiratoria en respiraciones por minuto",
                                                                    "example": 15
                                                                },
                                                                "temperature_status": {
                                                                    "type": "object",
                                                                    "description": "Estado basado en la temperatura",
                                                                    "properties": {
                                                                        "value": {
                                                                            "type": "string",
                                                                            "description": "Código del estado de temperatura",
                                                                            "example": "0"
                                                                        },
                                                                        "label": {
                                                                            "type": "string",
                                                                            "description": "Etiqueta del estado de temperatura",
                                                                            "example": "Crítico"
                                                                        }
                                                                    }
                                                                },
                                                                "heart_rate_status": {
                                                                    "type": "object",
                                                                    "description": "Estado basado en la frecuencia cardíaca",
                                                                    "properties": {
                                                                        "value": {
                                                                            "type": "string",
                                                                            "description": "Código del estado de frecuencia cardíaca",
                                                                            "example": "2"
                                                                        },
                                                                        "label": {
                                                                            "type": "string",
                                                                            "description": "Etiqueta del estado de frecuencia cardíaca",
                                                                            "example": "Estable"
                                                                        }
                                                                    }
                                                                },
                                                                "glucose_status": {
                                                                    "type": "object",
                                                                    "description": "Estado basado en el nivel de glucosa",
                                                                    "properties": {
                                                                        "value": {
                                                                            "type": "string",
                                                                            "description": "Código del estado de glucosa",
                                                                            "example": "2"
                                                                        },
                                                                        "label": {
                                                                            "type": "string",
                                                                            "description": "Etiqueta del estado de glucosa",
                                                                            "example": "Estable"
                                                                        }
                                                                    }
                                                                },
                                                                "oxygen_saturation_status": {
                                                                    "type": "object",
                                                                    "description": "Estado basado en la saturación de oxígeno",
                                                                    "properties": {
                                                                        "value": {
                                                                            "type": "string",
                                                                            "description": "Código del estado de saturación de oxígeno",
                                                                            "example": "2"
                                                                        },
                                                                        "label": {
                                                                            "type": "string",
                                                                            "description": "Etiqueta del estado de saturación de oxígeno",
                                                                            "example": "Estable"
                                                                        }
                                                                    }
                                                                },
                                                                "blood_pressure_status": {
                                                                    "type": "object",
                                                                    "description": "Estado basado en la presión arterial",
                                                                    "properties": {
                                                                        "value": {
                                                                            "type": "string",
                                                                            "description": "Código del estado de presión arterial",
                                                                            "example": "2"
                                                                        },
                                                                        "label": {
                                                                            "type": "string",
                                                                            "description": "Etiqueta del estado de presión arterial",
                                                                            "example": "Estable"
                                                                        }
                                                                    }
                                                                },
                                                                "respiratory_rate_status": {
                                                                    "type": "object",
                                                                    "description": "Estado basado en la frecuencia respiratoria",
                                                                    "properties": {
                                                                        "value": {
                                                                            "type": "string",
                                                                            "description": "Código del estado de frecuencia respiratoria",
                                                                            "example": "2"
                                                                        },
                                                                        "label": {
                                                                            "type": "string",
                                                                            "description": "Etiqueta del estado de frecuencia respiratoria",
                                                                            "example": "Estable"
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
                            }
                        }
                    },
                    "examples": {
                        "application/json": {
                            "summary": "Respuesta exitosa con datos de estado general",
                            "value": {
                                "status": "success",
                                "message": "Datos obtenidos exitosamente",
                                "data": {
                                    "status_summary": [
                                        {"status_code": "-1", "label": "Desconocido", "count": 0, "percent": 0},
                                        {"status_code": "0", "label": "Crítico", "count": 0, "percent": 0},
                                        {"status_code": "1", "label": "En Observación", "count": 1, "percent": 100.0},
                                        {"status_code": "2", "label": "Estable", "count": 0, "percent": 0}
                                    ],
                                    "states": [
                                        {
                                            "resident": {"id": 1, "name": "Aurora Ines Fajardo Perez"},
                                            "date": "2025-12-31 11:02:06",
                                            "status": {"value": "1", "label": "En Observación"},
                                            "anomaly": {
                                                "id": 12,
                                                "date": "2025-12-29 13:31:00",
                                                "user": {"id": 10, "name": "Dr. Carlos Ruiz"},
                                                "status": {"value": "1", "label": "En Observación"},
                                                "description": "El residente presenta fiebre persistente por más de 48 horas",
                                                "anomaly_level": {"id": 3, "name": "Moderado"}
                                            },
                                            "pain_scale": {
                                                "id": 1,
                                                "date": "2025-12-31 11:00:00",
                                                "user": {"id": 10, "name": "Dr. Carlos Ruiz"},
                                                "status": {"value": "1", "label": "En Observación"},
                                                "description": "Dolor moderado en la zona lumbar",
                                                "value_pain": 6,
                                                "pain_status": "Dolor moderado"
                                            },
                                            "neurological_assessment": {
                                                "id": 1,
                                                "date": "2025-12-31 11:00:00",
                                                "user": {"id": 10, "name": "Dr. Carlos Ruiz"},
                                                "status": {"value": "1", "label": "En Observación"},
                                                "description": "Reflejos normales, coordinación adecuada",
                                                "neurological_state": {"id": 2, "name": "Normal"}
                                            },
                                            "vital_signs": {
                                                "id": 1,
                                                "date": "2025-12-26 21:39:22",
                                                "user": {"id": 10, "name": "Dr. Carlos Ruiz"},
                                                "temperature": 37.5,
                                                "heart_rate": 78,
                                                "glucose": 88.0,
                                                "oxygen_saturation": 99,
                                                "blood_pressure": "118/78",
                                                "respiratory_rate": 15,
                                                "temperature_status": {"value": "0", "label": "Crítico"},
                                                "heart_rate_status": {"value": "2", "label": "Estable"},
                                                "glucose_status": {"value": "2", "label": "Estable"},
                                                "oxygen_saturation_status": {"value": "2", "label": "Estable"},
                                                "blood_pressure_status": {"value": "2", "label": "Estable"},
                                                "respiratory_rate_status": {"value": "2", "label": "Estable"}
                                            }
                                        }
                                    ]
                                }
                            }
                        }
                    }
                },
                "401": {
                    "description": "Token inválido o sesión no iniciada",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "example": "error"},
                            "message": {
                                "type": "string",
                                "example": "El usuario no tiene sessión iniciada",
                            },
                            "data": {"type": "null", "example": None},
                        },
                    },
                },
                "500": {
                    "description": "Error interno del servidor",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "example": "error"},
                            "message": {
                                "type": "string",
                                "example": "Error interno del servidor",
                            },
                            "data": {"type": "null", "example": None},
                        },
                    },
                },
            },
            "security": [{"bearerAuth": []}],
        }
    
    @http.route(
        "/api_serena/v1/get_general_condition_residents_of_residence",
        type='json',
        auth="none",
        methods=['POST'],
        csrf=False
    )
    def get_general_condition_residents_of_residence(self, **post):
        try:
            token = self._get_token()
            payload = self._get_payload(token)
            
            current_db = request.env.cr.dbname
            user_id = payload["user_id"]
            residence_id = payload["residence_id"]
            
            answer = []
            # Usar Registry directamente como recomienda el warning
            registry = Registry(current_db)
            
            with registry.cursor() as cr:
                env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
                ResUsers = env["res.users"].sudo()
                Resident = env["resident"].sudo()
                PainScale = env["pain.scale"].sudo()
                MedicalResidentState = env['medical.resident.state'].sudo()
                residents = Resident.search_read(
                        domain=[('residence_id','=',int(residence_id))],
                        fields=["id","name"]
                    )

                ids = []
                if residents:
                    ids = [d["id"] for d in residents]
                
                user = None
                # - Chequear que usuario tenga sessión activa
                user = ResUsers.browse(user_id)

                if not user:
                    raise AccessDenied("Usuario no encontrado")

                if not user.jwt_token or not user.token_expiration:
                    raise AccessDenied("El usuario no tiene sessión iniciada")
                
                # - Chequar que el usuario tenga los permisos para hacer
                if not self._check_user_permissions(user, 'medical.resident.state', self.CAN_READ, env):
                    raise AccessDenied("El usuario no tiene los permisos para esta operación")
                
                records = MedicalResidentState.get_last_states_by_resident_ids(ids)
                
                status_definitions = [
                    {'code': '-1', 'label': 'Desconocido'},
                    {'code': '0', 'label': 'Crítico'},
                    {'code': '1', 'label': 'En Observación'},
                    {'code': '2', 'label': 'Estable'}
                ]
                status_labels = {
                    '-1' : 'Desconocido',
                     '0' : 'Crítico',
                     '1' : 'En Observación',
                     '2' : 'Estable',
                }
                
                # Contar por estado
                status_counts = {}
                for status in status_definitions:
                    status_counts[status['code']] = {
                        'label': status['label'],
                        'count': 0,
                        'percent': 0
                    }
                    
                for r in records:
                    status_counts[r.general_status]['count'] = status_counts[r.general_status]['count'] + 1
                    status_counts[r.general_status]['percent'] = status_counts[r.general_status]['count'] / len(records) *100.00
            
                status_summary = []
                for status_code, data in status_counts.items():
                    status_summary.append({
                        'status_code': status_code,
                        'label': data['label'],
                        'count': data['count'],
                        'percent': data['percent']
                    })
                    
                states = []
                pain_status = dict(
                        PainScale._fields["pain_status"].selection
                    )
                
                for rec in records:
                    states.append({
                        "resident": {
                            "id": rec.resident_id.id,
                            "name": rec.resident_id.name,
                        },
                        "date": self._convert_timezone(user, rec.date), 
                        "status":{
                            "value": rec.general_status,
                            "label": status_labels[rec.general_status]
                        },
                        "anomaly":{
                            "id": rec.anomaly_id.id if rec.anomaly_id else False,
                            "date": self._convert_timezone(user, rec.anomaly_id.date) if rec.anomaly_id else False,
                            "user":{
                                "id": rec.anomaly_id.user_id.id if rec.anomaly_id else False,
                                "name": rec.anomaly_id.user_id.name if rec.anomaly_id else False,
                            },
                            "status":{
                                "value": rec.anomaly_id.general_status_resident if rec.anomaly_id else False,
                                "label": status_labels[rec.anomaly_id.general_status_resident] if rec.anomaly_id else False
                            },
                            "description": rec.anomaly_id.description if rec.anomaly_id else False,
                            "anomaly_level":{
                                "id": rec.anomaly_id.anomaly_level_id.id if rec.anomaly_id else False,
                                "name":rec.anomaly_id.anomaly_level_id.name if rec.anomaly_id else False
                            }
                        },
                        "pain_scale":{
                            "id": rec.pain_scale_id.id if rec.pain_scale_id else False,
                            "date": self._convert_timezone(user, rec.pain_scale_id.date) if rec.pain_scale_id else False,
                            "user":{
                                "id": rec.pain_scale_id.user_id.id if rec.pain_scale_id else False,
                                "name": rec.pain_scale_id.user_id.name if rec.pain_scale_id else False
                            },
                            "status":{
                                "value": rec.pain_scale_id.general_status_resident if rec.pain_scale_id else False,
                                "label": status_labels[rec.pain_scale_id.general_status_resident] if rec.pain_scale_id else False
                            },
                            "description": rec.pain_scale_id.description if rec.pain_scale_id else False,
                            "value_pain": rec.pain_scale_id.value_pain if rec.pain_scale_id else False, 
                            "pain_status": pain_status[rec.pain_scale_id.pain_status] if rec.pain_scale_id else False,
                        },
                        "neurological_assessment":{
                            "id": rec.neurological_assessment_id.id if rec.neurological_assessment_id else False,
                            "date": self._convert_timezone(user, rec.neurological_assessment_id.date) if rec.neurological_assessment_id else False,
                            "user":{
                                "id": rec.neurological_assessment_id.user_id.id if rec.neurological_assessment_id else False,
                                "name": rec.neurological_assessment_id.user_id.name if rec.neurological_assessment_id else False
                            },
                            "status":{
                                "value": rec.neurological_assessment_id.general_status_resident if rec.neurological_assessment_id else False,
                                "label": status_labels[rec.neurological_assessment_id.general_status_resident] if rec.neurological_assessment_id else False
                            },
                            "description": rec.neurological_assessment_id.description if rec.neurological_assessment_id else False,
                            "neurological_state":{
                                "id": rec.neurological_assessment_id.neurological_state_id.id if rec.neurological_assessment_id else False,
                                "name": rec.neurological_assessment_id.neurological_state_id.name if rec.neurological_assessment_id else False,
                            }
                        },
                        "vital_signs":{
                            "id": rec.vital_signs_id.id if rec.vital_signs_id else False,
                            "date": self._convert_timezone(user, rec.vital_signs_id.date) if rec.vital_signs_id else False,
                            "user":{
                                "id": rec.vital_signs_id.user_id.id if rec.vital_signs_id else False,
                                "name": rec.vital_signs_id.user_id.name if rec.vital_signs_id else False
                            },
                            "temperature": rec.vital_signs_id.temperature if rec.vital_signs_id else False,
                            "heart_rate": rec.vital_signs_id.heart_rate if rec.vital_signs_id else False,
                            "glucose": rec.vital_signs_id.glucose if rec.vital_signs_id else False,
                            "oxygen_saturation": rec.vital_signs_id.oxygen_saturation if rec.vital_signs_id else False,
                            "blood_pressure": rec.vital_signs_id.blood_pressure if rec.vital_signs_id else False,
                            "respiratory_rate": rec.vital_signs_id.respiratory_rate if rec.vital_signs_id else False,
                            "temperature_status": {
                                "value": rec.gsr_temperature if rec.vital_signs_id else False,
                                "label": status_labels[rec.gsr_temperature] if rec.vital_signs_id else False
                            },
                            "heart_rate_status": {
                                "value": rec.gsr_heart_rate if rec.vital_signs_id else False,
                                "label": status_labels[rec.gsr_heart_rate] if rec.vital_signs_id else False
                            },
                            "glucose_status": {
                                "value": rec.gsr_glucose if rec.vital_signs_id else False,
                                "label": status_labels[rec.gsr_glucose] if rec.vital_signs_id else False
                            },
                            "oxygen_saturation_status": {
                                "value": rec.gsr_oxygen_saturation if rec.vital_signs_id else False,
                                "label": status_labels[rec.gsr_oxygen_saturation] if rec.vital_signs_id else False
                            },
                            "blood_pressure_status": {
                                "value": rec.gsr_blood_pressure if rec.vital_signs_id else False,
                                "label": status_labels[rec.gsr_blood_pressure] if rec.vital_signs_id else False
                            },
                            "respiratory_rate_status": {
                                "value": rec.gsr_respiratory_rate if rec.vital_signs_id else False,
                                "label": status_labels[rec.gsr_respiratory_rate] if rec.vital_signs_id else False
                            },
                        },
                    })
            
            answer = {
                "status": "success",
                "message": "Datos obtenidos existosamente",
                "data": {
                    "status_summary": status_summary,
                    "states": states
                    },
            }
            return answer
        except Exception as e:
            return self._handle_error(e)