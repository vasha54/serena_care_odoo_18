import logging

from odoo import models, fields, api, _, tools
from odoo.exceptions import ValidationError, AccessDenied, UserError
from datetime import timedelta

_logger = logging.getLogger(__name__)


class UnifiedMedicalIndication(models.Model):
    _name = 'unified.medical.indication'
    _description = 'Indicaciones Médicas Unificadas'
    _auto = False  # Vista SQL, no crea tabla física

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