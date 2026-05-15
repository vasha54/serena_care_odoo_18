import json
import odoo
import logging
import jwt
import traceback
import yaml

from odoo import _, fields, http
from odoo.http import Response
from odoo.exceptions import AccessDenied, AccessError, UserError

from pytz import timezone
from datetime import datetime

from ..exceptions.exceptions import MissingMultipleParameterError, MissingParameterError 
from ..exceptions.exceptions import NotAccessResidence, AutheticateFailed
from ..exceptions.exceptions import DatabaseNotAviable, EmptyBodyInRequest

_logger = logging.getLogger(__name__)

class BaseAPIController(http.Controller):

    SECRET_KEY = "v#7P!x9A$gF2mZbR5kYq8tNs3Wu6cJdE1hT4oVlXp0yIjOeQrDaSzMfHnLwK_+CtB"
    ALGORITHM = "HS256"
    
    # Permisos individuales (bits individuales)
    CAN_NONE = 0          # 0000 - Sin permisos
    CAN_UNLINK = 1        # 0001 - Solo eliminar
    CAN_WRITE = 2         # 0010 - Solo modificar
    CAN_CREATE = 4        # 0100 - Solo crear
    CAN_READ = 8          # 1000 - Solo leer
    
    # Combinaciones de 2 permisos
    CAN_UNLINK_WRITE = 3          # 0011 - Eliminar + Modificar (1|2)
    CAN_UNLINK_CREATE = 5         # 0101 - Eliminar + Crear (1|4)
    CAN_UNLINK_READ = 9           # 1001 - Eliminar + Leer (1|8)
    CAN_WRITE_CREATE = 6          # 0110 - Modificar + Crear (2|4)
    CAN_WRITE_READ = 10           # 1010 - Modificar + Leer (2|8)
    CAN_CREATE_READ = 12          # 1100 - Crear + Leer (4|8)
    
    # Combinaciones de 3 permisos
    CAN_UNLINK_WRITE_CREATE = 7       # 0111 - Eliminar + Modificar + Crear (1|2|4)
    CAN_UNLINK_WRITE_READ = 11        # 1011 - Eliminar + Modificar + Leer (1|2|8)
    CAN_UNLINK_CREATE_READ = 13       # 1101 - Eliminar + Crear + Leer (1|4|8)
    CAN_WRITE_CREATE_READ = 14        # 1110 - Modificar + Crear + Leer (2|4|8)
    
    # Todos los permisos
    CAN_ALL = 15  # 1111 - Eliminar + Modificar + Crear + Leer (1|2|4|8)

    def _get_database(self):
        # Obtener la primera base de datos disponible
        db_names = odoo.service.db.list_dbs()
        if not db_names:
           _logger.error("No database available")
           raise DatabaseNotAviable()

        _logger.error(f"Count databases find :{len(db_names)}")
        # Usar la primera base de datos de la lista
        db_name = db_names[0]
        return db_name 
        
    def _get_env(self):
        try:
            db_name = self._get_database()
            # Acceder al registro de la base de datos
            registry = odoo.registry(db_name)
            with registry.cursor() as cr:
                self.ENV = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
                return self.ENV
        except Exception as e:
            return self._handle_error(e)

    def _get_json_data(self, _raw_data): 
        if not _raw_data:
            raise EmptyBodyInRequest()
        data = json.loads(_raw_data)
        return data  

    def _check_access_residences(self, _env, user_id, residence_id):
        employee = _env['hr.employee'].sudo().search_read(
            [
                ("user_id","=",user_id),
                ("alternative_residences_ids","in",residence_id),
            ])
        if not employee:
            raise NotAccessResidence()

    def _check_access_user_active(self, _env, _user_id):
        user = _env['res.users'].sudo().browse(_user_id)
        if not user:
            raise Exception("Usuario no encontrado")
        if not user.active:
            raise Exception("Usuario no activo")
        
    def _check_only_parameter(self, _parameter, **kwargs):
        if _parameter not in kwargs:
            raise MissingParameterError(_parameter)

    def _check_existence_parameters(self, _params, _data):
        for p in _params:
            if p not in _data:
                raise MissingParameterError(p)
        
    def _endpoint_not_yet_implemented(self):
        answer = {
            "status": "error",
            "message": "EndPoint de API aún no implementado",
            "data": None,
            "pagination": None,
        }
        return answer


    def _convert_to_iso(self, odoo_datetime):
        """Convierte datetime de Odoo a string ISO 8601"""
        if not odoo_datetime:
            return None

        # Si es un string (formato Odoo), convertir primero a objeto datetime
        if isinstance(odoo_datetime, str):
            dt_obj = fields.Datetime.from_string(odoo_datetime)
        else:  # Ya es un objeto datetime
            dt_obj = odoo_datetime

        return dt_obj.isoformat() + "Z"  # Añadir 'Z' para indicar UTC

    def _info_error(self, _exception):
        info_error = False
        type_exception = type(_exception).__name__
        message_exception = str(_exception)
        tb = traceback.extract_tb(_exception.__traceback__)
        if tb:
            file,line,function,text= tb[-1]
            info_error = {
                'type': type_exception,
                'message': message_exception,
                'file': file,
                'line':line,
                'function': function,
                'text': text,
            }
        else:
            info_error = {
                'type': type_exception,
                'message': message_exception,
                'file': None,
                'line':None,
                'function': None,
                'text': None,
            }
        return info_error

    def _handle_error(self, _exception, status=500):
        info_error = self._info_error(_exception)
        answer = {
            "status": "error",
            "message": str(_exception),
            "data": info_error,
            "pagination": None,
        }
        _logger.info(f"answer : {answer}")
        return answer

    def _handle_error_get(self, _exception, status=500):
        info_error = self._info_error(_exception)
        answer = {
            "status": "error",
            "message": str(_exception),
            "data": info_error,
            "pagination": None,
        }
        _logger.info(f"answer : {answer}")
        return Response(
            json.dumps(answer),
            status=status,
            headers={"Content-Type": "application/json"},
        )

    def _get_token(self):
        # Extraer token del encabezado Authorization
        auth_header = http.request.httprequest.headers.get('Authorization')
        if not auth_header or 'Bearer ' not in auth_header:
            raise Exception("Encabezado de autorización inválido")
            
        token = auth_header.split('Bearer ')[1].strip()
        return token

    def _get_payload(self,_token):
        payload = jwt.decode(_token, BaseAPIController.SECRET_KEY, algorithms=[BaseAPIController.ALGORITHM])
        return payload
                
    def _adjust_timezone(self, _user, _date):
        _logger.info(f"User tz: {_user.tz}")
        user_tz = timezone(_user.tz or 'UTC')
        utc_tz = timezone('UTC')
        # Convertir de la zona del usuario a UTC
        local_dt = user_tz.localize(datetime.strptime(_date, '%Y-%m-%d %H:%M:%S'))
        utc_dt = local_dt.astimezone(utc_tz)
        return utc_dt.strftime('%Y-%m-%d %H:%M:%S')
    
    def _convert_timezone(self, _user, _date):
        """
        Convierte un datetime de UTC a la zona horaria del usuario.
        
        Args:
            _user: objeto usuario con tz
            _date: objeto datetime (asume que está en UTC)
        """
        _logger.info(f"User tz: {_user.tz}")
        user_tz = timezone(_user.tz or 'UTC')
        utc_tz = timezone('UTC')
        
        # Asegurarnos de que el datetime tenga zona horaria UTC
        if _date.tzinfo is None:
            # Si es naive, asumir que está en UTC y añadir timezone UTC
            utc_dt = utc_tz.localize(_date)
        else:
            # Si ya tiene timezone, convertir a UTC por si acaso
            utc_dt = _date.astimezone(utc_tz)
        
        # Convertir a la zona del usuario
        user_dt = utc_dt.astimezone(user_tz)
        
        return user_dt.strftime('%Y-%m-%d %H:%M:%S')
    
    def _convert_timezone_date(self, _user, _date):
        """
        Convierte un datetime de UTC a la zona horaria del usuario.
        
        Args:
            _user: objeto usuario con tz
            _date: objeto datetime (asume que está en UTC)
        """
        _logger.info(f"User tz: {_user.tz}")
        user_tz = timezone(_user.tz or 'UTC')
        utc_tz = timezone('UTC')
        
        # Asegurarnos de que el datetime tenga zona horaria UTC
        if _date.tzinfo is None:
            # Si es naive, asumir que está en UTC y añadir timezone UTC
            utc_dt = utc_tz.localize(_date)
        else:
            # Si ya tiene timezone, convertir a UTC por si acaso
            utc_dt = _date.astimezone(utc_tz)
        
        # Convertir a la zona del usuario
        user_dt = utc_dt.astimezone(user_tz)
        
        return user_dt.strftime('%Y-%m-%d %H:%M:%S')
    
    def _convert_timezone_hours(self, _user, _date):
        """
        Convierte un datetime de UTC a la zona horaria del usuario.
        
        Args:
            _user: objeto usuario con tz
            _date: objeto datetime (asume que está en UTC)
        """
        _logger.info(f"User tz: {_user.tz}")
        user_tz = timezone(_user.tz or 'UTC')
        utc_tz = timezone('UTC')
        
        # Asegurarnos de que el datetime tenga zona horaria UTC
        if _date.tzinfo is None:
            # Si es naive, asumir que está en UTC y añadir timezone UTC
            utc_dt = utc_tz.localize(_date)
        else:
            # Si ya tiene timezone, convertir a UTC por si acaso
            utc_dt = _date.astimezone(utc_tz)
        
        # Convertir a la zona del usuario
        user_dt = utc_dt.astimezone(user_tz)
        
        return user_dt.strftime('%H:%M')

    def _check_user_permissions(self, _user, _model_name, _permission_bits, _env=None):
        """
        Función independiente para verificar permisos por bits
        
        Args:
            user (res.users): Objeto usuario
            model_name (str): Nombre del modelo
            permission_bits (int): Entero 0-15
            env (optional): Environment de Odoo
        
        Returns:
            bool: True si tiene todos los permisos requeridos
            
        Bit positions:
            0: unlink (eliminar)
            1: write (modificar)
            2: create (crear)
            3: read (leer)
            
        Ejemplo:
            permission_bits = 5 (0101) → bits 0 y 2 activos → verifica eliminar y crear
        """
        if not _env:
            from odoo.api import Environment
            # Si no se proporciona env, intenta obtenerlo del usuario
            _env = _user.env if hasattr(_user, 'env') else None
        
        if not _env:
            raise UserError("Se requiere un environment de Odoo")
        
        # Validaciones básicas
        if not 0 <= _permission_bits <= 15:
            return False
        
        try:
            # Obtener el modelo con el usuario específico
            Model = _env[_model_name].with_user(_user)
            
            # Mapeo de bits a operaciones
            operations = ['unlink', 'write', 'create', 'read']
            
            # Verificar cada permiso requerido
            for i, operation in enumerate(operations):
                if _permission_bits & (1 << i):  # Verificar si el bit está activo
                    try:
                        Model.check_access_rights(operation)
                    except AccessError:
                        return False
            
            return True
            
        except KeyError as k:
            info_error = self._info_error(k)
            _logger.error(f"{info_error}")
            return False
        except Exception as e:
            info_error = self._info_error(e)
            _logger.error(f"{info_error}")
            return False

    @http.route("/api_serena/v1/ping", type='json', auth='none')
    def ping(self):
        return {"status": "pong"} 
