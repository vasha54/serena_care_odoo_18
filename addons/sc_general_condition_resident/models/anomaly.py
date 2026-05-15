import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class Anomaly(models.Model):
    _inherit = 'anomaly'
    
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
        help='Estado general del residente basado en el nivel de anomalía'
    )
    
    # Campo entero para facilitar filtros y agrupaciones
    general_status_resident_int = fields.Integer(
        string='Estado General (Int)',
        compute='_compute_general_status_resident',
        store=True,
        readonly=True,
        help='Estado general del residente como entero: -1=Desconocido, 0=Crítico, 1=En Observación, 2=Estable'
    )
    
    @api.depends('anomaly_level_id')
    def _compute_general_status_resident(self):
        """
        Método computado que determina el estado general basado en anomaly_level_id
        Mapeo específico según los IDs XML del módulo sc_anomaly:
        - alevel_critical (Crítica) -> Crítico (0)
        - alevel_moderate (Moderada) -> En Observación (1)
        - alevel_mild (Leve) -> Estable (2)
        """
        for record in self:
            status = -1  # Valor por defecto: Desconocido
            
            if record.anomaly_level_id:
                # Obtener el XML ID del registro anomaly_level_id
                # Esto es necesario porque los nombres pueden cambiar con traducciones
                external_id = self._get_external_id_for_record(record.anomaly_level_id)
                
                if external_id:
                    # Extraer solo el nombre del ID sin el módulo
                    xml_id = external_id.split('.')[1] if '.' in external_id else external_id
                    
                    # Mapear según los IDs XML específicos
                    if xml_id == 'alevel_critical':
                        status = 0  # Crítico
                    elif xml_id == 'alevel_moderate':
                        status = 1  # En Observación
                    elif xml_id == 'alevel_mild':
                        status = 2  # Estable
                        
            # Asignar valores a ambos campos
            record.general_status_resident = str(status)
            record.general_status_resident_int = status
    
    def _get_external_id_for_record(self, record):
        """
        Método auxiliar para obtener el XML ID de un registro
        """
        try:
            # Buscar el XML ID en el sistema
            ir_model_data = self.env['ir.model.data'].search([
                ('model', '=', record._name),
                ('res_id', '=', record.id)
            ], limit=1)
            
            if ir_model_data:
                return ir_model_data.complete_name  # Devuelve 'module.xml_id'
            return None
        except Exception:
            return None
    
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