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
    pharmaceutical_form = fields.Char(
        related='medicament_id.pharmaceutical_form', 
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
    dosage_amount = fields.Float(
        string='Cantidad de Dosis',
        help="Cantidad de medicamento por administración"
    )
    dosage_unit = fields.Many2one(
        'uom.uom',
        string='Unidad de Dosis',
        help="Unidad de medida para la dosis (mg, mL, etc.)",
        required=True,
        ondelete='restrict',
        domain=[('is_uom_sc','=',True)],
        tracking=True, 
    )
    
    # Campos para frecuencia basadas en unidades de tiempo
    frequency_amount = fields.Integer(
        string='Cada',
        default=1,
        help="Cantidad de unidades de tiempo entre dosis",
        
    )
    frequency_unit = fields.Many2one(
        'uom.uom',
        string='Período',
        help="Unidad de tiempo para la frecuencia (horas, días, etc.)",
        domain=[('is_uom_sc','=',True)],
        
    )
    start_date_medication = fields.Datetime(
        string="Comienzo de la medicación",
        required=True
    )
    end_date_medication = fields.Datetime(
        string="Fin de la medicación",
        # Cambiado a no requerido para permitir medicamentos de por vida
        required=False
    )
    is_lifetime_medication = fields.Boolean(
        string="Medicación de por vida",
        default=False,
        help="Marcar si es un medicamento que se debe tomar de forma permanente"
    )
    is_prn = fields.Boolean(string="Es PRN", default=False, tracking=True,)

    @api.constrains('start_date_medication', 'end_date_medication', 'is_lifetime_medication', 'is_prn')
    def _check_dates(self):
        for record in self:
            current_datetime = fields.Datetime.now()
            
            # Validar fecha de inicio
            if record.start_date_medication and record.start_date_medication < current_datetime:
                raise ValidationError(_("La fecha de inicio no se puede establecer en el pasado."))
            
            if record .is_prn and not record.start_date_medication:
                raise ValidationError(_("La fecha de inicio debe establecerse"))
            
            if record.is_prn:
                continue
            
            # Validar fecha de fin si existe y no es medicación permanente
            if not record.is_lifetime_medication and record.end_date_medication:
                if record.start_date_medication and record.start_date_medication > record.end_date_medication:
                    raise ValidationError(_("La fecha de inicio debe ser anterior o igual a la fecha de finalización."))
            
            # Validar que no haya fecha de fin si es medicación permanente
            if record.is_lifetime_medication and record.end_date_medication:
                raise ValidationError(_("No puede establecer una fecha de finalización para una medicación de por vida."))

            # Validar que exista una fecha de finalización o una medicación de por vida
            if not record.is_lifetime_medication and not record.end_date_medication:
                raise ValidationError(_("La medicación debe ser de por vida o tener una fecha definalización."))


    def action_register_medical_medication(self):
        self.ensure_one()
        MedicalMedication = self.env['medical.medication'].sudo()
        MedicalMedication.create({
            'user_id': self.user_id.id,
            'resident_id': self.current_resident_id.id,
            'medicament_id': self.medicament_id.id,
            'pharmaceutical_form': self.pharmaceutical_form,
            'route_id': self.route_id.id,
            'dosage_amount':self.dosage_amount,
            'dosage_unit':self.dosage_unit.id,
            'frequency_amount':self.frequency_amount,
            'frequency_unit':self.frequency_unit.id,
            'start_date_medication': self.start_date_medication,
            'end_date_medication': self.end_date_medication,
            'is_lifetime_medication': self.is_lifetime_medication,
            'is_prn': self.is_prn,
            'active': True,
        })