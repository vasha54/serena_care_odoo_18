import os
import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

MAIL_SERVER_NAME = "Amazon SES - Serena Care"
DEFAULT_FROM_KEY = "mail.default.from"

def sync_mail_server(env):
    """
    Se ejecuta en:
    - instalación del módulo
    - actualización del módulo

    Sincroniza:
    - ir.mail_server
    - ir.config_parameter (mail.default.from)
    """
    _logger.warning("SYNC MAIL SERVER HOOK EXECUTED")
    
    # ---------- DEFAULT FROM EMAIL ----------
    default_from = os.getenv("DEFAULT_FROM_EMAIL")
    if default_from:
        param = env['ir.config_parameter'].sudo()
        param.set_param(DEFAULT_FROM_KEY, default_from)
        _logger.info("mail.default.from set to %s", default_from)
    else:
        _logger.warning("DEFAULT_FROM_EMAIL not defined")
    
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")

    if not smtp_user or not smtp_password:
        _logger.warning(
            "SMTP_USER or SMTP_PASSWORD not defined. "
            "Mail server will not be created/updated."
        )
        return

    values = {
        'name': MAIL_SERVER_NAME,
        'smtp_host': os.getenv(
            'SMTP_HOST', 'email-smtp.us-east-1.amazonaws.com'
        ),
        'smtp_port': int(os.getenv('SMTP_PORT', 587)),
        'smtp_encryption': os.getenv('SMTP_ENCRYPTION', 'starttls'),
        'smtp_user': smtp_user,
        'smtp_pass': smtp_password,
        'sequence': 10,
        'active': True,
    }

    MailServer = env['ir.mail_server']

    server = MailServer.search(
        [('name', '=', MAIL_SERVER_NAME)],
        limit=1
    )

    if server:
        server.write(values)
        _logger.info("SMTP mail server updated from environment variables")
    else:
        MailServer.create(values)
        _logger.info("SMTP mail server created from environment variables")
        
def uninstall_mail_server(env):
    
    server = env['ir.mail_server'].search(
        [('name', '=', MAIL_SERVER_NAME)]
    )

    if server:
        server.unlink()
        _logger.info("SMTP mail server removed on module uninstall")

