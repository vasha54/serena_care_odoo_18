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

class LaboratoryStudyAPIController(BaseAPIController):
    
    def doc_list_laboratory_study_this_resident(self):
        """
        Documentación Swagger para el método list_laboratory_study_this_resident

        Returns:
            dict: Documentación Swagger para el endpoint de listar los estudios
                de laboratorio de un residente
        """
        return {
            "tags": ["Laboratorio"],
            "summary": "Listar estudios de laboratorio de un residente",
            "description": """
            Endpoint para obtener el listado de los estudios de laboratorio
            asociados a un residente específico.

            Devuelve información básica del residente y un listado de archivos
            de laboratorio, incluyendo una **URL pública de descarga** para cada archivo.

            Requiere autenticación JWT válida.

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
                                "description": "Identificador del residente del cual se listarán los estudios de laboratorio",
                                "example": 6
                            }
                        },
                        "required": [
                            "resident_id"
                        ]
                    }
                }
            ],
            "responses": {
                "200": {
                    "description": "Listado de estudios de laboratorio obtenido exitosamente",
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
                                            "resident": {
                                                "type": "object",
                                                "description": "Información básica del residente",
                                                "properties": {
                                                    "id": {
                                                        "type": "integer",
                                                        "example": 6
                                                    },
                                                    "name": {
                                                        "type": "string",
                                                        "example": "Guadalupe Hernández Díaz"
                                                    }
                                                }
                                            },
                                            "count_files": {
                                                "type": "integer",
                                                "description": "Cantidad total de estudios de laboratorio",
                                                "example": 3
                                            },
                                            "files": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "id": {
                                                            "type": "integer",
                                                            "description": "Identificador del estudio de laboratorio",
                                                            "example": 12
                                                        },
                                                        "date": {
                                                            "type": "string",
                                                            "format": "date-time",
                                                            "description": "Fecha y hora del estudio de laboratorio",
                                                            "example": "2025-08-20 10:30:00"
                                                        },
                                                        "description": {
                                                            "type": "string",
                                                            "description": "Descripción del estudio de laboratorio",
                                                            "example": "Análisis de sangre completo"
                                                        },
                                                        "registered_by": {
                                                            "type": "string",
                                                            "description": "Nombre del usuario que registró el estudio",
                                                            "example": "Dr. Juan Pérez"
                                                        },
                                                        "filename": {
                                                            "type": "string",
                                                            "description": "Nombre del archivo del estudio de laboratorio",
                                                            "example": "hemograma.pdf"
                                                        },
                                                        "is_image": {
                                                            "type": "boolean",
                                                            "description": "Indica si el archivo es una imagen",
                                                            "example": False
                                                        },
                                                        "is_pdf": {
                                                            "type": "boolean",
                                                            "description": "Indica si el archivo es un PDF",
                                                            "example": True
                                                        },
                                                        "download_url": {
                                                            "type": "string",
                                                            "description": "URL pública para descargar el archivo sin autenticación",
                                                            "example": "http://localhost:8069/web/content/500?access_token=64219a33-69d4-4595-9510-d93422c3763c&download=true"
                                                        },
                                                        "attachment_id": {
                                                            "type": "integer",
                                                            "description": "Identificador del attachment asociado",
                                                            "example": 500
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
                "400": {
                    "description": "Parámetros faltantes o inválidos",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "example": "error"
                            },
                            "message": {
                                "type": "string",
                                "example": "Faltan parámetros requeridos"
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
                    "description": "Residente no encontrado",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "example": "error"
                            },
                            "message": {
                                "type": "string",
                                "example": "Residente no encontrado"
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
        "/api_serena/v1/list_laboratory_study_this_resident",
        type="json",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def list_laboratory_study_this_resident(self, **post):
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
                if not self._check_user_permissions(user, 'laboratory.file', self.CAN_READ, env):
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
                
                answer["resident"] ={
                    "id": resident.id,
                    "name":  resident.name,
                }
                    
                if resident.laboratory_file_ids:
                    data_files = []
                    for f in resident.laboratory_file_ids:
                        # Construir URL para descargar el archivo
                        download_url = ''
                        if f.laboratory_attachment_id:
                            att = f.laboratory_attachment_id
                            download_url = (
                                f"/web/content/{att.id}"
                                f"?access_token={att.access_token}"
                                # f"&download=true"
                            )
                        file_info = {
                            'id': f.id,
                            'date': self._convert_timezone(user,f.date) if f.date else None,
                            'description': f.description or '',
                            'registered_by': f.user_id.name if f.user_id else '',
                            'filename': f.laboratory_filename or '',
                            'is_image': f.is_image_file,
                            'is_pdf': f.is_pdf_file,
                            'download_url': request.httprequest.host_url[:-1] + download_url if download_url else '',
                            'attachment_id': f.laboratory_attachment_id.id if f.laboratory_attachment_id else None
                        }
                        data_files.append(file_info)
                    answer['count_files'] =len(data_files)
                    answer['files'] = data_files
                   
            answer = {
                    "status": "success",
                    "message": "Datos obtenidos existosamente",
                    "data": answer,
                }
            return answer
        except Exception as e:
            return self._handle_error(e)
