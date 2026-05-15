import re

from dateutil.relativedelta import relativedelta
from datetime import datetime
from pytz import timezone

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError

import logging
_logger = logging.getLogger(__name__)

class LaboratoryFile(models.Model):
    _inherit = 'laboratory.file'
    
    date_user = fields.Datetime(
        string='Fecha para el usuario',
        compute='_compute_date_user', 
        store=False,
    )
    
    download_url = fields.Char(
        string='URL de Descarga',
        compute='_compute_download_url',
        store=False
    )
    
    @api.depends('date')
    def _compute_date_user(self):
        user = self.env.user
        for r in self:
            if user and r.date:
                r.date_user = r._convert_timezone(user,r.date) 
                
    @api.depends('laboratory_attachment_id')
    def _compute_download_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for record in self:
            if record.laboratory_attachment_id:
                # Generar token si no existe
                if not record.laboratory_attachment_id.access_token:
                    record.laboratory_attachment_id.write({
                        'access_token': record.laboratory_attachment_id._generate_access_token()
                    })
                
                # Construir URL
                url = f"/web/content/{record.laboratory_attachment_id.id}"
                url += f"?access_token={record.laboratory_attachment_id.access_token}"
                
                record.download_url = f"{base_url}{url}"
            else:
                record.download_url = False
                
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
