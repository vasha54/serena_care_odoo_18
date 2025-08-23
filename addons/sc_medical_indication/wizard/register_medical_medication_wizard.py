import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class RegisterMedicalMedicationWizard(models.TransientModel):
    _name = 'register.medical.medication.wizard'
    _description = 'Registar Indicación Médica de Medicamentos en un Wizard desde la vista de residente'

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
    medicament_id = fields.Many2one(
        'medicament.product',
        string='Medicamento',
        requerid=True,
        ondelete='restrict',   
    )
    pharmaceutical_form_id = fields.Many2one(
        'pharmaceutical.form', 
        string='Forma Farmacéutica', 
        required=True, 
        ondelete='restrict',
    )
    route_id = fields.Many2one(
        'administration.route',
        string='Vía de Administración',
        required=True,
        ondelete='restrict', 
    )
    dosage = fields.Char(string='Dosis', required=True)
    concentration = fields.Char(string='Concentración', required=True)
    duration  = fields.Char(string='Duración del tratamiento', required=True)

    def action_register_medical_medication(self):
        self.ensure_one()
        MedicalMedication = self.env['medical.medication'].sudo()
        MedicalMedication.create({
            'date': self.date,
            'user_id': self.user_id.id,
            'resident_id': self.current_resident_id.id,
            'medicament_id': self.medicament_id.id,
            'pharmaceutical_form_id': self.pharmaceutical_form_id.id,
            'route_id': self.route_id.id,
            'dosage': self.dosage,
            'concentration': self.concentration,
            'duration': self.duration
        })