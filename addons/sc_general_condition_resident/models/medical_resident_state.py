import re
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError

import logging
_logger = logging.getLogger(__name__)

class GeneralStateResident(models.Model):
    _name = 'medical.resident.state'
    _description = 'Estado de General del Residente'

    resident_id = fields.Many2one(
        'resident', 
        string='Residente',
        required=True,
        ondelete='restrict',
    )
    date = fields.Datetime(
        string='Fecha/Hora', 
        default=fields.Datetime.now,
        required=True
    )
    general_status = fields.Selection(
        selection=[
            ('-1', 'Desconocido'),
            ('0', 'Crítico'),
            ('1', 'En Observación'),
            ('2', 'Estable'),
        ],
        string='Estado General del Residente',
        compute='_compute_general_status',
        store=True,
        readonly=True,
        help='Estado general del residente basado en la evaluación de diferentes pruebas'
    )
    
    # Campo entero para facilitar filtros y agrupaciones
    general_status_int = fields.Integer(
        string='Estado General (Int)',
        compute='_compute_general_status',
        store=True,
        readonly=True,
        help='Estado general del residente como entero: -1=Desconocido, 0=Crítico, 1=En Observación, 2=Estable'
    )
    anomaly_id = fields.Many2one(
        'anomaly', 
        string='Evaluación de Anomalía',
        help="Registro de la evaluación de anomalía tomada para calcular el estado",
        ondelete='restrict',
    )
    pain_scale_id = fields.Many2one(
        'pain.scale', 
        string='Evaluación del dolor',
        help="Registro de la evaluación de escala del dolor tomada para calcular el estado",
        ondelete='restrict',
    )
    neurological_assessment_id = fields.Many2one(
        'neurological.assessment', 
        string='Evaluación neurológica',
        help="Registro de la evaluación de neurológica tomada para calcular el estado",
        ondelete='restrict',
    )
    vital_signs_id = fields.Many2one(
        'vital.signs', 
        string='Muestras de signos vitales',
        help="Registro de la muestra de signos vitales tomada para calcular el estado",
        ondelete='restrict',
    )
    
    status_anomaly_id = fields.Selection(
        related='anomaly_id.general_status_resident', 
        string="Evaluación de Anomalía",
        readonly=True,
        help="Estado del residente basado en la evaluación de anomalía"
    )
    
    status_pain_scale_id = fields.Selection(
        related='pain_scale_id.general_status_resident', 
        string="Evaluación de Dolor",
        readonly=True,
        help="Estado del residente basado en la evaluación de dolor"
    )
    
    status_neurological_assessment_id = fields.Selection(
        related='neurological_assessment_id.general_status_resident', 
        string="Evaluación Neurológica",
        readonly=True,
        help="Estado del residente basado en la evaluación neurológica"
    )
    
    status_vital_signs_id = fields.Selection(
        related='vital_signs_id.general_status_resident', 
        string="Evaluación Signos Vitales",
        readonly=True,
        help="Estado del residente basado en la evaluación de signos vitales"
    )
    
    date_anomaly_id = fields.Datetime(
        related='anomaly_id.date', 
        string="Fecha",
        readonly=True
    )
    description_anomaly_id = fields.Text(
        related='anomaly_id.description', 
        string="Descripción",
        readonly=True
    )
    user_id_anomaly_id = fields.Many2one(
        related='anomaly_id.user_id', 
        string="Registrado",
        readonly=True
    )
    anomaly_level_id_anomaly_id = fields.Many2one(
        related='anomaly_id.anomaly_level_id', 
        string="Nivel de la anomalía",
        readonly=True
    )
    
    date_pain_scale_id = fields.Datetime(
        related='pain_scale_id.date', 
        string="Fecha",
        readonly=True
    )
    description_pain_scale_id = fields.Text(
        related='pain_scale_id.description', 
        string="Descripción",
        readonly=True
    )
    user_id_pain_scale_id = fields.Many2one(
        related='pain_scale_id.user_id', 
        string="Resgistrado",
        readonly=True
    )
    value_pain_pain_scale_id = fields.Integer(
        string='Valor cuantitativo',
        related='pain_scale_id.value_pain', 
        readonly=True
    )
    pain_status_pain_scale_id = fields.Selection(
        string='Estado del dolor',
        related='pain_scale_id.pain_status', 
        readonly=True
    )
    
    date_neurological_assessment_id = fields.Datetime(
        related='neurological_assessment_id.date', 
        string="Fecha",
        readonly=True
    )
    description_neurological_assessment_id = fields.Text(
        related='neurological_assessment_id.description', 
        string="Desccripción",
        readonly=True
    )
    user_id_neurological_assessment_id = fields.Many2one(
        related='neurological_assessment_id.user_id', 
        string="Registrado",
        readonly=True
    )
    neurological_state_id_neurological_assessment_id = fields.Many2one(
        related='neurological_assessment_id.neurological_state_id', 
        string="Estado Neurológico",
        readonly=True
    )
    
    # Signos Vitales
    user_id_signs_id = fields.Many2one(
        related='vital_signs_id.user_id', 
        string="Registrado",
        readonly=True
    )
    date_vital_signs_id = fields.Datetime(
        related='vital_signs_id.date', 
        string="Fecha",
        readonly=True
    )
    temperature_vital_signs_id = fields.Float(
        related='vital_signs_id.temperature', 
        string="Temperatura",
        readonly=True
    )
    heart_rate_vital_signs_id = fields.Integer(
        string='Frecuencia Cardíaca (lpm)',
        related='vital_signs_id.heart_rate', 
        readonly=True
    )
    systolic_vital_signs_id = fields.Integer(
        string='Tensión Arterial Sistólica (mmHg)',
        related='vital_signs_id.systolic', 
        readonly=True
    )
    diastolic_vital_signs_id = fields.Integer(
        string='Tensión Arterial Diastólica (mmHg)', 
        related='vital_signs_id.diastolic', 
        readonly=True
    )
    respiratory_rate_vital_signs_id = fields.Integer(
        string='Frecuencia Respiratoria (rpm)', 
        related='vital_signs_id.respiratory_rate', 
        readonly=True
    )
    oxygen_saturation_vital_signs_id = fields.Integer(
        string='Oxigenación (%)',  
        related='vital_signs_id.oxygen_saturation', 
        readonly=True
    )
    glucose_vital_signs_id = fields.Float(
        string='Glucosa (mg/dL)', 
        related='vital_signs_id.glucose', 
        readonly=True
    )
    grip_strength_vital_signs_id = fields.Float(
        string='Fuerza de Presión (kg)', 
        related='vital_signs_id.grip_strength', 
        readonly=True
    )
    blood_pressure_vital_signs_id = fields.Char(
        string='Tensión Arterial',
        related='vital_signs_id.blood_pressure', 
        readonly=True
    )
    gsr_temperature = fields.Selection(
        string='Estado General del Residente por Temperatura',
        related='vital_signs_id.gsr_temperature', 
        readonly=True
    )
    gsr_oxygen_saturation = fields.Selection(
        string='Estado General del Residente por Saturación de Oxígeno',
        related='vital_signs_id.gsr_oxygen_saturation', 
        readonly=True
    )
    gsr_glucose = fields.Selection(
        string='Estado General del Residente por Glucosa',
        related='vital_signs_id.gsr_glucose', 
        readonly=True
    )
    gsr_heart_rate = fields.Selection(
        string='Estado General del Residente por Frecuencia Cardíaca',
        related='vital_signs_id.gsr_heart_rate', 
        readonly=True
    )
    gsr_blood_pressure = fields.Selection(
        string='Estado General del Residente por Tensión Arterial',
        related='vital_signs_id.gsr_blood_pressure', 
        readonly=True
    )
    gsr_respiratory_rate = fields.Selection(
        string='Estado General del Residente por Frecuencia Respiratoria',
        related='vital_signs_id.gsr_respiratory_rate', 
        readonly=True
    )
    
    
    @api.depends('vital_signs_id','neurological_assessment_id','pain_scale_id','anomaly_id')
    def _compute_general_status(self):
        for record in self:
            if record.vital_signs_id and record.neurological_assessment_id and \
                record.pain_scale_id and record.anomaly_id:
                t_points  = 0
                t_aspects = 9
                t_points = t_points + record.anomaly_id.general_status_resident_int
                t_points = t_points + record.pain_scale_id.general_status_resident_int
                t_points = t_points + record.neurological_assessment_id.general_status_resident_int
                t_points = t_points + record.vital_signs_id.gsr_temperature_int
                t_points = t_points + record.vital_signs_id.gsr_oxygen_saturation_int
                t_points = t_points + record.vital_signs_id.gsr_glucose_int
                t_points = t_points + record.vital_signs_id.gsr_blood_pressure_int
                t_points = t_points + record.vital_signs_id.gsr_respiratory_rate_int
                t_points = t_points + record.vital_signs_id.gsr_heart_rate_int
                
                media = t_points // t_aspects
                record.general_status_int = media
                record.general_status = str(media) 
            else:
                record.general_status_int = -1
                record.general_status = str(-1) 
                
    @api.depends('resident_id')
    def _compute_display_name(self):
        for r in self:
            r.display_name = f"Estado general de {r.resident_id.name}"
            
    @api.model
    def get_last_states_by_resident_ids(self, resident_ids):
        """Obtiene el último registro de estado general por cada residente en la lista"""
        # Paso 1: Encontrar la fecha máxima por residente
        query = """
            SELECT resident_id, MAX(date) as max_date
            FROM medical_resident_state
            WHERE resident_id IN %s
            GROUP BY resident_id
        """
        
        self.env.cr.execute(query, (tuple(resident_ids),))
        max_dates = self.env.cr.dictfetchall()
        
        # Paso 2: Obtener los registros completos correspondientes
        records = self.env['medical.resident.state']
        for item in max_dates:
            record = self.search([
                ('resident_id', '=', item['resident_id']),
                ('date', '=', item['max_date'])
            ], limit=1)
            if record:
                records += record
        
        return records
    
    @api.model
    def create(self, values):
        records = super().create(values)
        # Crear log de auditoría para cada registro creado
        for record in records:
            self.env['audit.log'].sudo().crud_audit_log(record, 'medical.resident.state', 'create')
        return records
    
    def write(self, vals):
        # Guardar estado anterior para detectar cambios (opcional, mejora la calidad del detalle)
        old_values = {}
        for record in self:
            old_values[record.id] = {
                field: record[field] for field in vals if field in record._fields and not record._fields[field].compute
            }
        result = super().write(vals)
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
            self.env['audit.log'].sudo().crud_audit_log(record, 'medical.resident.state', 'write', extra_details=details)
        return result
    
    def unlink(self):
        # Antes de eliminar, crear logs para cada registro
        for record in self:
            self.env['audit.log'].sudo().crud_audit_log(record, 'medical.resident.state', 'unlink')
        return super().unlink()