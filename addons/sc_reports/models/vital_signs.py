import logging

from dateutil.relativedelta import relativedelta
from datetime import datetime
from pytz import timezone

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)

class VitalSigns(models.Model):
    _inherit = 'vital.signs'
    
    date_user = fields.Datetime(
        string='Fecha para el usuario',
        compute='_compute_date_user', 
        store=False,
    )
    general_status_resident_label = fields.Char(
        string='Estado General del Residente',
        compute='_compute_general_status_resident_label',
        store=False
    )
    
    @api.depends('general_status_resident')
    def _compute_general_status_resident_label(self):
        for record in self:
            record.general_status_resident_label = dict(
                self._fields['general_status_resident'].selection
            ).get(record.general_status_resident, '') 
    
    @api.depends('date')
    def _compute_date_user(self):
        user = self.env.user
        for r in self:
            if user and r.date:
                r.date_user = r._convert_timezone(user,r.date) 
                
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