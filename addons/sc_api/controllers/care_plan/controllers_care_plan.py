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

class CarePlanController(BaseAPIController):

    def doc_get_care_plan_this_resident(self):
        """
        Documentación Swagger para el método get_care_plan_this_resident
        
        Returns:
            dict: Documentación Swagger para el endpoint de obtener plan de cuidado de un residente
        """
        return {
            "tags": ["Planes de Cuidado"],
            "summary": "Obtener el plan de cuidado de un residente específico",
            "description": """
            Endpoint para obtener el plan de cuidado completo asociado a un residente específico.
            Requiere autenticación JWT válida y que el residente pertenezca a la residencia del usuario autenticado.

            **Cabeceras requeridas:**
            - Content-Type: application/json
            - Authorization: Bearer <token_jwt>

            **Parámetros requeridos en el cuerpo:**
            - resident_id: ID del residente para el cual se desea obtener el plan de cuidado
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
                    "description": "Parámetros requeridos para obtener el plan de cuidado del residente",
                    "schema": {
                        "type": "object",
                        "required": ["resident_id"],
                        "properties": {
                            "resident_id": {
                                "type": "integer",
                                "description": "ID del residente para el cual se desea obtener el plan de cuidado",
                                "example": 4
                            }
                        },
                        "example": {
                            "resident_id": 4
                        }
                    }
                }
            ],
            "responses": {
                "200": {
                    "description": "Plan de cuidado obtenido exitosamente",
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
                                        "example": "Datos obtenidos existosamente"
                                    },
                                    "data": {
                                        "type": "object",
                                        "properties": {
                                            "id": {
                                                "type": "integer",
                                                "description": "Identificador numérico del plan de cuidado",
                                                "example": 2
                                            },
                                            "resident": {
                                                "type": "object",
                                                "description": "Información básica del residente",
                                                "properties": {
                                                    "id": {
                                                        "type": "integer",
                                                        "description": "ID del residente",
                                                        "example": 4
                                                    },
                                                    "name": {
                                                        "type": "string",
                                                        "description": "Nombre completo del residente",
                                                        "example": "Ana Flores Ramírez"
                                                    }
                                                }
                                            },
                                            "diagnosis": {
                                                "type": "string",
                                                "description": "Diagnóstico médico del residente",
                                                "example": "fsfsfsf"
                                            },
                                            "care_level": {
                                                "type": "object",
                                                "description": "Nivel de cuidado asignado al residente",
                                                "properties": {
                                                    "id": {
                                                        "type": "integer",
                                                        "description": "ID del nivel de cuidado",
                                                        "example": 2
                                                    },
                                                    "name": {
                                                        "type": "string",
                                                        "description": "Nombre del nivel de cuidado",
                                                        "example": "Medio"
                                                    }
                                                }
                                            },
                                            "plan_activity": {
                                                "type": "array",
                                                "description": "Lista de actividades del plan de cuidado",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "id": {
                                                            "type": "integer",
                                                            "description": "ID de la actividad del plan",
                                                            "example": 2
                                                        },
                                                        "dependency_level": {
                                                            "type": "object",
                                                            "description": "Nivel de dependencia para esta actividad",
                                                            "properties": {
                                                                "id": {
                                                                    "type": "integer",
                                                                    "description": "ID del nivel de dependencia",
                                                                    "example": 2
                                                                },
                                                                "name": {
                                                                    "type": "string",
                                                                    "description": "Nombre del nivel de dependencia",
                                                                    "example": "Medio"
                                                                }
                                                            }
                                                        },
                                                        "activity_type": {
                                                            "type": "object",
                                                            "description": "Tipo de actividad",
                                                            "properties": {
                                                                "id": {
                                                                    "type": "integer",
                                                                    "description": "ID del tipo de actividad",
                                                                    "example": 4
                                                                },
                                                                "name": {
                                                                    "type": "string",
                                                                    "description": "Nombre del tipo de actividad",
                                                                    "example": "Deambulación y traslado"
                                                                }
                                                            }
                                                        },
                                                        "goal": {
                                                            "type": "array",
                                                            "description": "Metas asociadas a esta actividad",
                                                            "items": {
                                                                "type": "object",
                                                                "properties": {
                                                                    "id": {
                                                                        "type": "integer",
                                                                        "description": "ID de la meta",
                                                                        "example": 2
                                                                    },
                                                                    "name": {
                                                                        "type": "string",
                                                                        "description": "Descripción de la meta",
                                                                        "example": "Detectar oportunamente fuentes de riesgo de accidentes o caídas."
                                                                    }
                                                                }
                                                            }
                                                        },
                                                        "action": {
                                                            "type": "array",
                                                            "description": "Acciones a realizar para esta actividad",
                                                            "items": {
                                                                "type": "object",
                                                                "properties": {
                                                                    "id": {
                                                                        "type": "integer",
                                                                        "description": "ID de la acción",
                                                                        "example": 21
                                                                    },
                                                                    "name": {
                                                                        "type": "string",
                                                                        "description": "Descripción de la acción",
                                                                        "example": "Promover la movilidad."
                                                                    }
                                                                }
                                                            }
                                                        },
                                                        "observation": {
                                                            "type": "array",
                                                            "description": "Observaciones para esta actividad",
                                                            "items": {
                                                                "type": "object",
                                                                "properties": {
                                                                    "id": {
                                                                        "type": "integer",
                                                                        "description": "ID de la observación",
                                                                        "example": 18
                                                                    },
                                                                    "name": {
                                                                        "type": "string",
                                                                        "description": "Descripción de la observación",
                                                                        "example": "Riesgo de caída, raspadura y daños cutáneos."
                                                                    }
                                                                }
                                                            }
                                                        },
                                                        "result": {
                                                            "type": "array",
                                                            "description": "Resultados esperados para esta actividad",
                                                            "items": {
                                                                "type": "object",
                                                                "properties": {
                                                                    "id": {
                                                                        "type": "integer",
                                                                        "description": "ID del resultado",
                                                                        "example": 6
                                                                    },
                                                                    "name": {
                                                                        "type": "string",
                                                                        "description": "Descripción del resultado",
                                                                        "example": "Mantener la movilidad para mejorar la autonomía y evitar el deterioro físico que acompaña la edad."
                                                                    }
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            },
                                            "count_activitys": {
                                                "type": "integer",
                                                "description": "Número total de actividades en el plan",
                                                "example": 2
                                            },
                                            "count_dependency_level": {
                                                "type": "integer",
                                                "description": "Número total de niveles de dependencia",
                                                "example": 2
                                            },
                                            "count_goals": {
                                                "type": "integer",
                                                "description": "Número total de metas en el plan",
                                                "example": 3
                                            },
                                            "count_actions": {
                                                "type": "integer",
                                                "description": "Número total de acciones en el plan",
                                                "example": 3
                                            },
                                            "count_observations": {
                                                "type": "integer",
                                                "description": "Número total de observaciones en el plan",
                                                "example": 4
                                            },
                                            "count_results": {
                                                "type": "integer",
                                                "description": "Número total de resultados en el plan",
                                                "example": 2
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "400": {
                    "description": "Parámetros inválidos o faltantes",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "example": "error"
                            },
                            "message": {
                                "type": "string",
                                "example": "Parámetro resident_id es requerido"
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
                                "example": "Usuario no autenticado"
                            },
                            "data": {
                                "type": "null",
                                "example": None
                            }
                        }
                    }
                },
                "403": {
                    "description": "Acceso denegado - El residente no pertenece a la residencia del usuario",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "example": "error"
                            },
                            "message": {
                                "type": "string",
                                "example": "El residente no se encuentra en la residencia en la que usuario se autenticó"
                            },
                            "data": {
                                "type": "null",
                                "example": None
                            }
                        }
                    }
                },
                "404": {
                    "description": "Plan de cuidado no encontrado",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "example": "error"
                            },
                            "message": {
                                "type": "string",
                                "example": "El residente no tiene plan de cuidado asignado"
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
        "/api_serena/v1/care_plan_this_resident",
        type='json', 
        auth="none", 
        methods=['POST'], 
        csrf=False
    )
    def get_care_plan_this_resident(self, **post):
        try:
            parameters = [
                "resident_id",
            ]
            token = self._get_token()
            payload = self._get_payload(token)
            data = self._get_json_data(request.httprequest.data)
            self._check_existence_parameters(parameters, data)

            current_db = request.env.cr.dbname
            user_id = payload["user_id"]
            residence_id = payload["residence_id"]
            resident_id = data["resident_id"]

            answer = {}
            # Usar Registry directamente como recomienda el warning
            registry = Registry(current_db)
            with registry.cursor() as cr:
                env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
                CarePlan = env["care.plan"].sudo()
                ResUsers = env["res.users"].sudo()
                Resident = env["resident"].sudo()
                resident = None
                user = None
                # - Chequear que usuario tenga sessión activa
                user = ResUsers.browse(user_id)

                if not user:
                    raise AccessDenied("Usuario no encontrado")

                if not user.jwt_token or not user.token_expiration:
                    raise AccessDenied("El usuario no tiene sessión iniciada")

                # - Chequar que el usuario tenga los permisos para hacer
                if not self._check_user_permissions(user, 'care.plan', self.CAN_READ, env):
                    raise AccessDenied("El usuario no tiene los permisos para esta operación")

                # - Chequear que exista el residente
                resident = Resident.browse(resident_id)

                if not resident:
                    raise AccessDenied("Residente no encontrado")

                # - Chequear que en la residencia donde trabaja el usuario
                # en esta sessión sea la misma que la del residente
                if resident and resident.residence_id.id != residence_id:
                    raise AccessDenied(
                        "El residente no se encuentra en la residencia en el \
que usuario se autentico"
                    )

                # Listar todas las mediciones del balance hídrico del residente
                answer = []
                records_cp = CarePlan.search_read(
                    domain=[("resident_id", "=", resident_id)],
                    fields=[
                        "id",
                        "resident",
                        "diagnosis",
                        "care_level",
                        "plan_activity",
                        "count_activitys",
                        "count_dependency_level",
                        "count_goals",
                        "count_actions",
                        "count_observations",
                        "count_results"
                    ],
                )
                if not records_cp:
                   raise Exception("El residente no tiene plan de cuidado asignado") 

                answer = records_cp[0]                    

            answer = {
                "status": "success",
                "message": "Datos obtenidos existosamente",
                "data": answer,
            }
            return answer
        except Exception as e:
            return self._handle_error(e)