import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)

class MedicalMedication(models.Model):
    _name = 'medical.medication'
    _description = 'Indicación de Medicamento'
    _inherit = 'medical.indication'  # Hereda campos comunes
    
    active = fields.Boolean(
        string='Activa',
        default=True,
        help="Si está marcado, la indicación se considera activa."
    )
    medicament_id = fields.Many2one(
        'medicament.product',
        string='Medicamento',
        required=True,  # Corregí "requerid" a "required"
        ondelete='restrict',  
        tracking=True, 
    )
    pharmaceutical_form = fields.Char(
        related='medicament_id.pharmaceutical_form',
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
    is_prn = fields.Boolean(string="Es PRN", default=False, tracking=True,)
 
    @api.depends('dosage_amount', 'dosage_unit')
    def _compute_dosage(self):
        for record in self:
            if record.dosage_amount and record.dosage_unit:
                record.dosage_str = f"{record.dosage_amount} {record.dosage_unit.name}"
            else:
                record.dosage_str = False
    
    @api.depends('frequency_amount', 'frequency_unit')
    def _compute_frequency(self):
        for record in self:
            if record.frequency_amount and record.frequency_unit:
                record.frequency_str = f"{record.frequency_amount} {record.frequency_unit.name}"
            else:
                record.frequency_str = False

    @api.depends('start_date_medication', 'end_date_medication', 'is_lifetime_medication','is_prn')
    def _compute_period_medication(self):
        for record in self:
            if record.is_prn:
                record.period_medication = _("Siempre que sea necesario por una urgencia")
                continue
            if record.is_lifetime_medication and record.start_date_medication:
                start_str = record.start_date_medication.strftime('%Y-%m-%d %H:%M')
                record.period_medication = _("Desde %s (medicación permanente)") % start_str
            elif record.start_date_medication and record.end_date_medication:
                start_str = record.start_date_medication.strftime('%Y-%m-%d %H:%M')
                end_str = record.end_date_medication.strftime('%Y-%m-%d %H:%M')
                record.period_medication = _("Desde %s hasta %s") % (start_str, end_str)
            elif record.start_date_medication:
                start_str = record.start_date_medication.strftime('%Y-%m-%d %H:%M')
                record.period_medication = _("Desde %s") % start_str
            else:
                record.period_medication = False

    @api.depends(
        'medicament_id', 
        'pharmaceutical_form', 
        'route_id', 
        'dosage_amount',
        'dosage_unit',
        'frequency_amount',
        'frequency_unit',
        'start_date_medication',
        'end_date_medication',
        'is_lifetime_medication',
        'is_prn'
    )
    def _compute_note(self):
        for record in self:
            parts = []
            
            # Información del medicamento
            if record.medicament_id:
                parts.append(_("Medicamento: %s") % record.medicament_id.name)
            
            # Forma farmacéutica
            if record.pharmaceutical_form:
                parts.append(_("Forma farmacéutica: %s") % record.pharmaceutical_form)
            
            # Vía de administración
            if record.route_id:
                parts.append(_("Vía de administración: %s") % record.route_id.name)
            
            # Dosificación
            if record.dosage_amount and record.dosage_unit:
                parts.append(_("Dosis: %s %s") % (record.dosage_amount, record.dosage_unit.name))
             
            # Frecuencia
            if not record.is_prn:
                if record.frequency_amount and record.frequency_unit:
                    parts.append(_("Frecuencia: Cada %s %s") % (record.frequency_amount, record.frequency_unit.name))
            else:
                parts.append(_("Frecuencia: Siempre que sea necesario por una urgencia"))   
            
            # Período de administración
            if not record.is_prn:
                if record.is_lifetime_medication and record.start_date_medication:
                    start_str = record.start_date_medication.strftime('%Y-%m-%d %H:%M')
                    parts.append(_("Período: Desde %s (medicación permanente)") % start_str)
                elif record.start_date_medication and record.end_date_medication:
                    start_str = record.start_date_medication.strftime('%Y-%m-%d %H:%M')
                    end_str = record.end_date_medication.strftime('%Y-%m-%d %H:%M')
                    parts.append(_("Período: Desde %s hasta %s") % (start_str, end_str))
                elif record.start_date_medication:
                    start_str = record.start_date_medication.strftime('%Y-%m-%d %H:%M')
                    parts.append(_("Período: Desde %s") % start_str)
            else:
                if record.start_date_medication:
                    start_str = record.start_date_medication.strftime('%Y-%m-%d %H:%M')
                    parts.append(_("Período: Desde %s") % start_str)
            
            # Unir todas las partes
            record.note = '\n'.join(parts)

    @api.constrains('dosage_amount')
    def _check_dosage_amount(self):
        for record in self:
            if record.dosage_amount and record.dosage_amount <= 0.0:
                raise ValidationError(_("La dosis debe ser un valor positivo."))

    @api.constrains('start_date_medication', 'end_date_medication', 'is_lifetime_medication','is_prn')
    def _check_dates(self):
        for record in self:
            current_datetime = fields.Datetime.now()
            
            # Validar fecha de inicio
            if record.start_date_medication and record.start_date_medication < current_datetime:
                raise ValidationError(_("La fecha de inicio no se puede establecer en el pasado."))
            
            if record.is_prn and not record.start_date_medication:
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

    @api.onchange('is_lifetime_medication')
    def _onchange_is_lifetime_medication(self):
        """Limpiar fecha de finalización si es medicación permanente"""
        if self.is_lifetime_medication:
            self.end_date_medication = False
            
    def write(self, vals):
        # Guardar estado anterior para detectar cambios (opcional, mejora la calidad del detalle)
        old_values = {}
        for record in self:
            old_values[record.id] = {
                field: record[field] for field in vals if field in record._fields and not record._fields[field].compute
            }
        result = super(MedicalMedication, self).write(vals)
        # Después de la escritura, crear logs con los campos modificados
        for record in self:
            changed_fields = []
            for field, new_val in vals.items():
                if field in old_values.get(record.id, {}):
                    old_val = old_values[record.id][field]
                    if old_val != record[field]:
                        changed_fields.append(f"{field}: {old_val!r} -> {record[field]!r}")
                else:
                    # Campo no almacenado o no presente en el registro anterior, se registra igual
                    changed_fields.append(f"{field}: {record[field]!r}")
            if changed_fields:
                details = "Campos modificados: " + "; ".join(changed_fields)
            else:
                details = "Modificación sin cambios detectados"
            self.env['audit.log'].sudo().crud_audit_log(record, 'medical.medication', 'write', extra_details=details)
        return result
    
    def unlink(self):
        # Validar que no se elimine si la fecha de inicio ya pasó
        now = fields.Datetime.now()
        for record in self:
            if record.start_date_medication and now >= record.start_date_medication:
                raise UserError(_(
                    "No se puede eliminar la indicación porque su fecha de inicio (%s) ya ha pasado o es la actual."
                ) % record.start_date_medication)
        # Antes de eliminar, crear logs para cada registro
        for record in self:
            self.env['audit.log'].sudo().crud_audit_log(record, 'medical.medication', 'unlink')
        return super(MedicalMedication, self).unlink()
    
    @api.depends('resident_id')
    def _compute_display_name(self):
        for r in self:
            r.display_name = f"Indicación médica de medicamento de {r.resident_id.name}"
            
    @api.model
    def create(self, values):
        records = super(MedicalMedication, self).create(values)
        # Crear log de auditoría para cada registro creado
        for record in records:
            self.env['audit.log'].sudo().crud_audit_log(record, 'medical.medication', 'create')
        return records