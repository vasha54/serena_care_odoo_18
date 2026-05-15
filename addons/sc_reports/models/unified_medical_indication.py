import logging
from datetime import timedelta
from pytz import timezone

from odoo import models, fields, api, _, tools
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class UnifiedMedicalIndication(models.Model):
    _inherit = 'unified.medical.indication'
    
    date_user = fields.Datetime(
        string='Fecha para el usuario',
        compute='_compute_date_user', 
        store=False,
    )
    indication_type_label = fields.Char(
        string='Tipo de Indicación',
        compute='_compute_indication_type_label',
        store=False
    )
    
    @api.depends('create_date')
    def _compute_date_user(self):
        user = self.env.user
        for r in self:
            if user and r.create_date:
                r.date_user = r._convert_timezone(user,r.create_date)
                
    @api.depends('indication_type')
    def _compute_indication_type_label(self):
        for record in self:
            record.indication_type_label = dict(
                self._fields['indication_type'].selection
            ).get(record.indication_type, '') 
                
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

    indication_id = fields.Integer(string='ID')
    indication_type = fields.Selection([
        ('general', 'General'),
        ('medication', 'Medicamento')
    ], string='Tipo')
    create_date = fields.Datetime(string='Fecha')
    user_id = fields.Many2one('res.users', string='Doctor')
    resident_id = fields.Many2one('resident', string='Residente')
    note = fields.Text(string='Indicación')

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""
            CREATE OR REPLACE VIEW {self._table} AS (
                SELECT 
                    'general_' || id AS id,
                    id AS indication_id,
                    'general' AS indication_type,
                    create_date,
                    user_id,
                    resident_id,
                    note
                FROM medical_indication
                UNION ALL
                SELECT 
                    'medication_' || id AS id,
                    id AS indication_id,
                    'medication' AS indication_type,
                    create_date,
                    user_id,
                    resident_id,
                    note
                FROM medical_medication
            )
        """)

    @api.model
    def open_record(self):
        return self.action_open_indication()
    
    def action_open_indication(self):
        self.ensure_one()
        target = self.env.context.get('open_target', 'current')
        if self.indication_type == 'general':
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'medical.indication',
                'res_id': self.indication_id,
                'views': [(False, 'form')],
                'view_mode': 'form',
                'target': target,
            }
        elif self.indication_type == 'medication':
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'medical.medication',
                'res_id': self.indication_id,
                'views': [(False, 'form')],
                'view_mode': 'form',
                'target': target,
            }
        else:
            raise UserError(_('Tipo de indicación médica no reconocido'))

    def action_create_general(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'medical.indication',
            'view_mode': 'form',
            'target': 'current',
            'context': self.env.context,
        }

    def action_create_medication(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'medical.medication',
            'view_mode': 'form',
            'target': 'current',
            'context': self.env.context,
        }