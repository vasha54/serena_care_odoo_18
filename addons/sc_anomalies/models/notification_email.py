import re
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError

import logging
_logger = logging.getLogger(__name__)

class NotificationEmail(models.Model):
    _name = 'notification.email'
    _description = 'Correo de notificación de anomalía críticas'

    active = fields.Boolean(string='Activo', default=True)
    email = fields.Char(string="Correo electrónico", required=True)

    @api.constrains('email')
    def _check_email_format(self):
        """Valida que el campo email tenga un formato correcto"""
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        for record in self:
            if record.email:
                if not re.match(email_regex, record.email.strip()):
                    raise ValidationError(
                        _('Formato de correo electrónico inválido: %s') % record.email
                    )
    
    @api.depends('email')
    def _compute_display_name(self):
        for r in self:
            r.display_name = f"Dirección de correo: {r.email}"