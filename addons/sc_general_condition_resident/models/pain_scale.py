import re
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError

import logging
_logger = logging.getLogger(__name__)

class PainScale(models.Model):
    _inherit = 'pain.scale'
    
    # Campo computado de selección
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
        help='Estado general del residente basado en la escala del dolor'
    )
    
    # Campo entero para facilitar filtros y agrupaciones
    general_status_resident_int = fields.Integer(
        string='Estado General (Int)',
        compute='_compute_general_status_resident',
        store=True,
        readonly=True,
        help='Estado general del residente como entero: -1=Desconocido, 0=Crítico, 1=En Observación, 2=Estable'
    )
    
    @api.depends('value_pain')
    def _compute_general_status_resident(self):
        """
        Método computado que determina el estado general basado en value_pain:
        - De 9 a 10 -> Crítico (0)
        - De 3 a 8 (Moderada) -> En Observación (1)
        - De 0 a 2 -> Estable (2)
        """
        for record in self:
            status = -1  # Valor por defecto: Desconocido
            
            if 0 <= record.value_pain and record.value_pain <= 2:
                status = 2
            elif 3 <= record.value_pain and record.value_pain <= 8:
                status = 1
            elif 9 <= record.value_pain and record.value_pain <= 10:
                status = 0
                        
            # Asignar valores a ambos campos
            record.general_status_resident = str(status)
            record.general_status_resident_int = status
    
    
    # Método para mostrar el estado en vistas
    def get_status_display(self):
        """Devuelve el texto del estado para usar en vistas"""
        status_map = {
            '-1': _('Desconocido'),
            '0': _('Crítico'),
            '1': _('En Observación'),
            '2': _('Estable'),
        }
        return status_map.get(self.general_status_resident, _('Desconocido'))