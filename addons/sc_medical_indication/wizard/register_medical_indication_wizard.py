import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class RegisterMedicalIndicationWizard(models.TransientModel):
    _name = 'register.medical.indication.wizard'
    _description = 'Registar Indicación Médica General en un Wizard desde la vista de residente'

    date = fields.Datetime(
        string='Fecha/Hora', 
        default=fields.Datetime.now,
        required=True
    )
    user_id = fields.Many2one(
        'res.users', 
        string='Doctor',
        default=lambda self: self.env.user,
        required=True,
        ondelete='restrict',
    )
    current_resident_id = fields.Many2one(
        'resident', 
        string='Residente',
        required=True,
        default=lambda self: self.env.context.get('active_id')
    )
    note = fields.Text(string='Indicación', required=True)

    def action_register_medical_indication(self):
        self.ensure_one()
        MedicalIndication = self.env['medical.indication'].sudo()
        MedicalIndication.create({
            'user_id': self.user_id.id,
            'resident_id': self.current_resident_id.id,
            'note': self.note,
            'active': True,
        })
