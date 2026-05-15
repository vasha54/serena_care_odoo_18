import re
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError

import logging

from pytz import timezone
from datetime import datetime

_logger = logging.getLogger(__name__)

class Anomaly(models.Model):
    _name = 'anomaly'
    _description = 'Anomalía'

    resident_id = fields.Many2one(
        'resident', 
        string='Residente',
        required=True,
        ondelete='restrict',
    )
    residence_id =  fields.Many2one(
        string="Residencia",
        related='resident_id.residence_id', 
        readonly=True
    )
    date = fields.Datetime(
        string='Fecha/Hora', 
        default=fields.Datetime.now,
        required=True
    )
    description = fields.Text(string='Descripción')
    user_id = fields.Many2one(
        'res.users', 
        string='Registrado por', 
        default=lambda self: self.env.user,
        required=True,
        ondelete='restrict',
    )
    anomaly_level_id = fields.Many2one(
        'anomaly.level', 
        string="Nivel de la anomalía", 
        required=True,
        domain=[('active','=',True)]
    )

    @api.depends('resident_id','user_id')
    def _compute_display_name(self):
        for r in self:
            r.display_name = f"Anomalía de {r.resident_id.name}"
            
    @api.model
    def create(self, values):
        record = super().create(values)
        if record:
            critical_level = self.env.ref(
                'sc_anomalies.alevel_critical',
                raise_if_not_found=False
                )
            if critical_level and record.anomaly_level_id.id == critical_level.id:
                _logger.info("Anomalía CRÍTICA detectada, enviando notificación")
                record._send_critical_anomaly_email() 
        return record
    
    def _get_default_from_email(self):
        return (
            self.env['ir.config_parameter']
            .sudo()
            .get_param('mail.default.from')
            or self.env.company.email
            or 'no-reply@idooprod.com'
        )

    
    def _send_critical_anomaly_email(self):
        self.ensure_one()

        NotificationEmail = self.env['notification.email']

        active_emails = NotificationEmail.search([('active', '=', True)])

        recipient_list = [
            e.email.strip()
            for e in active_emails
            if e.email
        ]

        if not recipient_list:
            _logger.warning("No hay correos activos para notificación")
            return
        
        email_from = self._get_default_from_email()
        _logger.info("Correo FROM usado: %s", email_from)
        
        mail_values = {
            'subject': _('🚨 Anomalía CRÍTICA registrada. Serena-Care'),
            'email_from': email_from,
            'email_to': ','.join(recipient_list),
            'body_html': f"""
                <p><strong>Se ha registrado una anomalía crítica.</strong></p>
                <ul>
                    <li><strong>Residente:</strong> {self.resident_id.name}</li>
                    <li><strong>Residencia:</strong> {self.resident_id.residence_id.name}</li>
                    <li><strong>Fecha:</strong> {self._convert_timezone(self.user_id,self.date)}</li>
                    <li><strong>Registrado por:</strong> {self.user_id.name}</li>
                </ul>
                <p>{self.description or ''}</p>
            """,
        }

        mail = self.env['mail.mail'].create(mail_values)
        try:
            mail.send(auto_commit=True)
        except Exception as e:
            _logger.error("Error enviando email crítico: %s", e)
            
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
        
        return user_dt.strftime('%d/%m/%Y %H:%M:%S')
        