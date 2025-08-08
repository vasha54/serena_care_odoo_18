import json
import odoo
import logging

from odoo import _, fields, http
from odoo.http import Response
from odoo.exceptions import AccessDenied

from ..exceptions.exceptions import MissingMultipleParameterError, MissingParameterError 
from ..exceptions.exceptions import NotAccessResidence, AutheticateFailed
from ..exceptions.exceptions import DatabaseNotAviable, EmptyBodyInRequest

_logger = logging.getLogger(__name__)

class BaseAPIController(http.Controller):

    SECRET_KEY = "v#7P!x9A$gF2mZbR5kYq8tNs3Wu6cJdE1hT4oVlXp0yIjOeQrDaSzMfHnLwK_+CtB"
    ALGORITHM = "HS256"
    ENV = None

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
        return Response(
            json.dumps(answer),
            status=501,
            headers={"Content-Type": "application/json"},
        )

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

    def _handle_error(self, error, status=500):
        answer = {
            "status": "error",
            "message": str(error),
            "data": None,
            "pagination": None,
        }
        _logger.info(f"answer : {answer}")
        return Response(
            json.dumps(answer),
            status=status,
            headers={"Content-Type": "application/json"},
        )

    @http.route("/api_serena/ping", type='json', auth='none')
    def ping(self):
        return {"status": "pong"} 