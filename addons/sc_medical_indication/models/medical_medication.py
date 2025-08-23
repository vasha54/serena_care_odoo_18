import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)

class MedicalMedication(models.Model):
    _name = 'medical.medication'
    _description = 'Indicación de Medicamento'
    _inherit = 'medical.indication'  # Hereda campos comunes
    
    medicament_id = fields.Many2one(
        'medicament.product',
        string='Medicamento',
        requerid=True,
        ondelete='restrict',  
        tracking=True, 
    )
    pharmaceutical_form_id = fields.Many2one(
        related='medicament_id.pharmaceutical_form_id',
        readonly=True,
        string='Forma Farmacéutica', 
        required=True, 
        ondelete='restrict',
        tracking=True
    )
    route_id = fields.Many2one(
        'administration.route',
        string='Vía de Administración',
        required=True,
        ondelete='restrict',
        tracking=True, 
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

    # Campos para frecuencia basada en unidades de tiempo
    frequency_amount = fields.Integer(
        string='Cada',
        default=1.0,
        help="Cantidad de unidades de tiempo entre dosis",
        required=True,
    )
    frequency_unit = fields.Many2one(
        'uom.uom',
        string='Período',
        help="Unidad de tiempo para la frecuencia (horas, días, etc.)",
        domain=[('is_uom_sc','=',True)],
        required=True,
    )
    start_date_medication = fields.Datetime(string="Comienzo de la medicación",required=True)
    end_date_medication = fields.Datetime(string="Fin de la medicación",required=True)

    note = fields.Text(
        string='Indicación',
        compute='_compute_note',
        store=True,
        tracking=True,
    )
    frequency_str = fields.Text(
        string='Frecuencia',
        compute='_compute_frequency',
        store=True,
        tracking=True,
    )
    dosage_str = fields.Text(
        string='Dosis',
        compute='_compute_dosage',
        store=True,
        tracking=True,
    )
    period_medication = fields.Text(
        string='Período',
        compute='_compute_period_medication',
        store=True,
        tracking=True,
    )
 
    @api.depends(
        'dosage_amount',
        'dosage_unit'
    )
    def _compute_dosage(self):
        for record in self:
            record.dosage_str = f"{record.dosage_amount} {record.dosage_unit.name}"
    
    @api.depends(
        'frequency_amount',
        'frequency_unit'
    )
    def _compute_frequency(self):
        for record in self:
            record.frequency_str = f"{record.frequency_amount} {record.frequency_unit.name}"

    @api.depends(
        'start_date_medication',
        'end_date_medication'
    )
    def _compute_period_medication(self):
        for record in self:
            if record.start_date_medication and record.end_date_medication:
                start_str = record.start_date_medication.strftime('%Y-%m-%d %H:%M')
                end_str = record.end_date_medication.strftime('%Y-%m-%d %H:%M')
                record.period_medication = _("Desde %s hasta %s") % (start_str, end_str)
            else:
                record.period_medication = False

    @api.depends(
        'medicament_id', 
        'pharmaceutical_form_id', 
        'route_id', 
        'dosage_amount',
        'dosage_unit',
        'frequency_amount',
        'frequency_unit',
        'start_date_medication',
        'end_date_medication'
    )
    def _compute_note(self):
        for record in self:
            parts = []
            
            # Información del medicamento
            if record.medicament_id:
                parts.append(_("Medicamento: %s") % record.medicament_id.name)
            
            # Forma farmacéutica
            if record.pharmaceutical_form_id:
                parts.append(_("Forma farmacéutica: %s") % record.pharmaceutical_form_id.name)
            
            # Vía de administración
            if record.route_id:
                parts.append(_("Vía de administración: %s") % record.route_id.name)
            
            # Dosificación
            if record.dosage_amount and record.dosage_unit:
                parts.append(_("Dosis: %s %s") % (record.dosage_amount, record.dosage_unit.name))
             
            # Frecuencia
            if record.frequency_amount and record.frequency_unit:
                parts.append(_("Frecuencia: Cada %s %s") % (record.frequency_amount, record.frequency_unit.name))
            
            # Período de administración
            if record.start_date_medication and record.end_date_medication:
                start_str = record.start_date_medication.strftime('%Y-%m-%d %H:%M')
                end_str = record.end_date_medication.strftime('%Y-%m-%d %H:%M')
                parts.append(_("Período: Desde %s hasta %s") % (start_str, end_str))
            
            # Unir todas las partes
            record.note = '\n'.join(parts)

    @api.constrains('dosage_amount')
    def _check_dosage_amount(self):
        for record in self:
            if record.dosage_amount <= 0.0:
                raise ValidationError(_("La dosis debe ser un valor positivo."))

    @api.constrains('start_date_medication', 'end_date_medication')
    def _check_dates(self):
        for record in self:
            if record.start_date_medication and record.end_date_medication:

                current_datetime = fields.Datetime.now()
            
                # Check if start date is in the future
                if record.start_date_medication and record.start_date_medication < current_datetime:
                    raise ValidationError(_("La fecha de inicio no se puede establecer en el pasado."))


                if record.start_date_medication > record.end_date_medication:
                    raise ValidationError(_("La fecha de inicio debe ser anterior o igual a la fecha de finalización."))
