import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)

class VitalSigns(models.Model):
    _inherit = 'vital.signs'
    
    general_status_resident = fields.Selection(
        selection=[
            ('-1', 'Desconocido'),
            ('0', 'Crítico'),
            ('1', 'En Observación'),
            ('2', 'Estable'),
        ],
        string='Estado General del Residente',
        compute='_compute_general_status_resident',
        store=True,
        readonly=True,
        help='Estado general del residente basado en el registro de los signos vitales'
    )
    
    # Campo entero para facilitar filtros y agrupaciones
    general_status_resident_int = fields.Integer(
        string='Estado General (Int)',
        compute='_compute_general_status_resident',
        store=True,
        readonly=True,
        help='Estado general del residente como entero: -1=Desconocido, 0=Crítico, 1=En Observación, 2=Estable'
    )
    
    gsr_temperature = fields.Selection(
        selection=[
            ('-1', 'Desconocido'),
            ('0', 'Crítico'),
            ('1', 'En Observación'),
            ('2', 'Estable'),
        ],
        string='Estado General del Residente',
        compute='_compute_general_status_resident',
        store=True,
        readonly=True,
        help='Estado general del residente basado en la temperatura'
    )
    
    gsr_temperature_int = fields.Integer(
        string='Estado General (Int)',
        compute='_compute_general_status_resident',
        store=True,
        readonly=True,
        help='Estado general del residente como entero: -1=Desconocido, 0=Crítico, 1=En Observación, 2=Estable'
    )
    
    gsr_oxygen_saturation = fields.Selection(
        selection=[
            ('-1', 'Desconocido'),
            ('0', 'Crítico'),
            ('1', 'En Observación'),
            ('2', 'Estable'),
        ],
        string='Estado General del Residente',
        compute='_compute_general_status_resident',
        store=True,
        readonly=True,
        help='Estado general del residente basado en la temperatura'
    )
    
    gsr_oxygen_saturation_int = fields.Integer(
        string='Estado General (Int)',
        compute='_compute_general_status_resident',
        store=True,
        readonly=True,
        help='Estado general del residente como entero: -1=Desconocido, 0=Crítico, 1=En Observación, 2=Estable'
    )
    
    gsr_glucose = fields.Selection(
        selection=[
            ('-1', 'Desconocido'),
            ('0', 'Crítico'),
            ('1', 'En Observación'),
            ('2', 'Estable'),
        ],
        string='Estado General del Residente',
        compute='_compute_general_status_resident',
        store=True,
        readonly=True,
        help='Estado general del residente basado en la glucosa'
    )
    
    gsr_glucose_int = fields.Integer(
        string='Estado General (Int)',
        compute='_compute_general_status_resident',
        store=True,
        readonly=True,
        help='Estado general del residente como entero: -1=Desconocido, 0=Crítico, 1=En Observación, 2=Estable'
    )
    
    gsr_heart_rate = fields.Selection(
        selection=[
            ('-1', 'Desconocido'),
            ('0', 'Crítico'),
            ('1', 'En Observación'),
            ('2', 'Estable'),
        ],
        string='Estado General del Residente',
        compute='_compute_general_status_resident',
        store=True,
        readonly=True,
        help='Estado general del residente basado en la Frecuencia Cardíaca'
    )
    
    gsr_heart_rate_int = fields.Integer(
        string='Estado General (Int)',
        compute='_compute_general_status_resident',
        store=True,
        readonly=True,
        help='Estado general del residente como entero: -1=Desconocido, 0=Crítico, 1=En Observación, 2=Estable'
    )
    
    gsr_blood_pressure = fields.Selection(
        selection=[
            ('-1', 'Desconocido'),
            ('0', 'Crítico'),
            ('1', 'En Observación'),
            ('2', 'Estable'),
        ],
        string='Estado General del Residente',
        compute='_compute_general_status_resident',
        store=True,
        readonly=True,
        help='Estado general del residente basado en la Tensión Arterial'
    )
    
    gsr_blood_pressure_int = fields.Integer(
        string='Estado General (Int)',
        compute='_compute_general_status_resident',
        store=True,
        readonly=True,
        help='Estado general del residente como entero: -1=Desconocido, 0=Crítico, 1=En Observación, 2=Estable'
    )
    
    gsr_respiratory_rate = fields.Selection(
        selection=[
            ('-1', 'Desconocido'),
            ('0', 'Crítico'),
            ('1', 'En Observación'),
            ('2', 'Estable'),
        ],
        string='Estado General del Residente',
        compute='_compute_general_status_resident',
        store=True,
        readonly=True,
        help='Estado general del residente basado en la Frecuencia Respiratoria'
    )
    
    gsr_respiratory_rate_int = fields.Integer(
        string='Estado General (Int)',
        compute='_compute_general_status_resident',
        store=True,
        readonly=True,
        help='Estado general del residente como entero: -1=Desconocido, 0=Crítico, 1=En Observación, 2=Estable'
    )
    
    def _compute_general_status_temperature(self):
        """
        Método computado que determina el estado general basado en los 
        valores de la temperatura:
        - Menor que 35,8 ó mayor que 37,3 -> Crítico (0)
        - De 35,8 a 35,9 ó de 37 a 37,3 -> En Observación (1)
        - De 36 a 36,9 -> Estable (2)
        """
        self.ensure_one()
        if self.temperature < 35.8 or self.temperature > 37.3:
            return 0  # Crítico
        elif (35.8 <= self.temperature <= 35.9) or (37 <= self.temperature <= 37.3):
            return 1  # En Observación
        elif 36 <= self.temperature <= 36.9:
            return 2  # Estable
        return -1  # Valor fuera de rangos definidos
    
    def _compute_general_status_oxygen_saturation(self):
        """
        Método computado que determina el estado general basado en los 
        valores de la saturación del oxigeno:
        - Menor que 90 -> Crítico (0)
        - De 90 a 94 -> En Observación (1)
        - Mayor o igual que 95 -> Estable (2)
        """
        self.ensure_one()
        if self.oxygen_saturation < 90:
            return 0
        elif 90 <= self.oxygen_saturation <= 94:
            return 1
        elif 95 <= self.oxygen_saturation:
            return 2 
        return -1
    
    def _compute_general_status_glucose(self):
        """
        Método computado que determina el estado general basado en los 
        valores de la glucosa:
        - Menos que 55 o mayor que 139 -> Crítico (0)
        - De 55 a 69 ó de 100 a 139 -> En Observación (1)
        - De 70 a 99 -> Estable (2)
        """
        self.ensure_one()
        if self.glucose < 55 or self.glucose > 139:
            return 0  # Crítico
        elif (55 <= self.glucose <= 69) or (100 <= self.glucose <= 139):
            return 1  # En Observación
        elif 70 <= self.glucose <= 99:
            return 2  # Estable
        return -1  # Valor fuera de rangos definidos
    
    def _compute_general_status_heart_rate(self):
        """
        Método computado que determina el estado general basado en los 
        valores de la Frecuencia Cardíaca:
        - Menos que 55 o mayor que 105 -> Crítico (0)
        - De 55 a 59 ó de 101 a 105 -> En Observación (1)
        - De 60 a 100 -> Estable (2)
        """
        self.ensure_one()
        if self.heart_rate < 55 or self.heart_rate > 105:
            return 0  # Crítico
        elif (55 <= self.heart_rate <= 59) or (101 <= self.heart_rate <= 105):
            return 1  # En Observación
        elif 60 <= self.heart_rate <= 100:
            return 2  # Estable
        return -1  # Valor fuera de rangos definidos
    
    def _compute_general_status_blood_pressure(self):
        """
        Método computado que determina el estado general basado en los 
        valores de la Tensión Arterial (sistólica / diastólica):
        * Para sistólica (systolic mayor)
        - Menor que 100 o mayor que 140 -> Crítico (0)
        - De 100 a 109 o de 131 a 140 -> En Observación (1)
        - De 110 a 130 -> Estable (2)
        * Para diastólica (diastolic menor)
        - Menor que 60 o mayor que 90 -> Crítico (0)
        - De 60 a 69 o de 81 a 90 -> En Observación (1)
        - De 70 a 80 -> Estable (2)
        
        Si los dos son iguales se mantiene el estado pero
        Estable + Observación = Estable
        Observacion + Critico = Critico
        Estable + Critico = critico
        
        Usar self.systolic y self.diastolic
        """
        self.ensure_one()
    
        # Clasificar la presión sistólica
        if self.systolic < 100 or self.systolic > 140:
            systolic_status = 0  # Crítico
        elif (100 <= self.systolic <= 109) or (131 <= self.systolic <= 140):
            systolic_status = 1  # En Observación
        elif 110 <= self.systolic <= 130:
            systolic_status = 2  # Estable
        else:
            systolic_status = -1  # Valor fuera de rangos
        
        # Clasificar la presión diastólica
        if self.diastolic < 60 or self.diastolic > 90:
            diastolic_status = 0  # Crítico
        elif (60 <= self.diastolic <= 69) or (81 <= self.diastolic <= 90):
            diastolic_status = 1  # En Observación
        elif 70 <= self.diastolic <= 80:
            diastolic_status = 2  # Estable
        else:
            diastolic_status = -1  # Valor fuera de rangos
        
        # Si alguno es -1, no podemos determinar el estado
        if systolic_status == -1 or diastolic_status == -1:
            return -1
        
        # Si ambos tienen el mismo estado, mantenerlo
        if systolic_status == diastolic_status:
            return systolic_status
        
        # Combinar estados según las reglas especificadas
        # Estable + Observación = Estable (2)
        if (systolic_status == 2 and diastolic_status == 1) or \
           (systolic_status == 1 and diastolic_status == 2):
            return 2
        
        # Cualquier combinación con Crítico (0) da Crítico
        # Esto cubre: Observación + Crítico y Estable + Crítico
        if systolic_status == 0 or diastolic_status == 0:
            return 0
        
        # Si llegamos aquí, es una combinación no contemplada
        return -1
    
    def _compute_general_status_respiratory_rate(self):
        """
        Método computado que determina el estado general basado en los 
        valores de la Frecuencia Respiratoria:
        - Menos que 10 o mayor que 20 -> Crítico (0)
        - De 10 a 11 ó de 19 a 20 -> En Observación (1)
        - De 12 a 18 -> Estable (2)
        """
        self.ensure_one()
        if self.respiratory_rate < 10 or self.respiratory_rate > 20:
            return 0  # Crítico
        elif (10 <= self.respiratory_rate <= 11) or (19 <= self.respiratory_rate <= 20):
            return 1  # En Observación
        elif 12 <= self.respiratory_rate <= 18:
            return 2  # Estable
        return -1
    
    @api.depends('temperature','oxygen_saturation','glucose','systolic','diastolic','blood_pressure','respiratory_rate')
    def _compute_general_status_resident(self):
        """
        Método computado que determina el estado general basado en los 
        valores de los signos vitales:
        """
        for record in self:
            status_temperature = record._compute_general_status_temperature()
            status_oxygen_saturation = record._compute_general_status_oxygen_saturation()
            status_glucose = record._compute_general_status_glucose()
            status_heart_rate = record._compute_general_status_heart_rate()
            status_blood_pressure = record._compute_general_status_blood_pressure()
            status_respiratory_rate = record._compute_general_status_respiratory_rate()  
            
            record.gsr_temperature = str(status_temperature)
            record.gsr_temperature_int = status_temperature
            record.gsr_oxygen_saturation = str(status_oxygen_saturation)
            record.gsr_oxygen_saturation_int = status_oxygen_saturation
            record.gsr_glucose = str(status_glucose)
            record.gsr_glucose_int = status_glucose
            record.gsr_blood_pressure = str(status_blood_pressure)
            record.gsr_blood_pressure_int = status_blood_pressure 
            record.gsr_respiratory_rate = str(status_respiratory_rate)
            record.gsr_respiratory_rate_int = status_respiratory_rate
            record.gsr_heart_rate = str(status_heart_rate)
            record.gsr_heart_rate_int = status_heart_rate 
            
            status = [
                        status_temperature, 
                        status_oxygen_saturation, 
                        status_glucose,
                        status_heart_rate,
                        status_blood_pressure,
                        status_respiratory_rate
                    ]
            status_media = sum(status) // len(status) 
            
            record.general_status_resident = str(status_media)
            record.general_status_resident_int = status_media
            
            
            