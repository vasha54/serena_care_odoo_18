import logging
from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class Resident(models.Model):
    _inherit = 'resident'
    
    medical_resident_state_ids = fields.One2many(
        'medical.resident.state', 
        'resident_id',
        string='Comprobaciones del Estado General',
        help="Listado de las comprobaciones del Estado General al residente"
    )
    
    last_anomaly_id = fields.Many2one(
        'anomaly',
        string='Última Anomalía',
        compute='_compute_last_anomaly',
        store=True,
        help="La anomalía más reciente del residente"
    )
    
    last_pain_scale_id = fields.Many2one(
        'pain.scale',
        string='Última evaluación de la escala del dolor',
        compute='_compute_last_pain_scale',
        store=True,
        help="La evaluación de la escala del dolor más reciente del residente"
    )
    
    last_neurological_assessment_id = fields.Many2one(
        'neurological.assessment',
        string='Última evaluación neurológica',
        compute='_compute_last_neurological_assessment',
        store=True,
        help="La evaluación neurológica más reciente del residente"
    )
    
    last_vital_signs_id = fields.Many2one(
        'vital.signs',
        string='Último registro de signos vitales',
        compute='_compute_last_vital_signs',
        store=True,
        help="El registro de signos vitales más reciente del residente"
    )
    
    @api.depends('anomaly_ids', 'anomaly_ids.date')
    def _compute_last_anomaly(self):
        for record in self:
            if record.anomaly_ids:
                # Ordenar por fecha descendente y tomar la primera
                last_anomaly = record.anomaly_ids.sorted(
                    key=lambda a: a.date, 
                    reverse=True
                )[0]
                record.last_anomaly_id = last_anomaly.id
            else:
                record.last_anomaly_id = False
                
    @api.depends('pain_scale_ids', 'pain_scale_ids.date')
    def _compute_last_pain_scale(self):
        for record in self:
            if record.pain_scale_ids:
                # Ordenar por fecha descendente y tomar la primera
                last_pain_scale = record.pain_scale_ids.sorted(
                    key=lambda a: a.date, 
                    reverse=True
                )[0]
                record.last_pain_scale_id = last_pain_scale.id
            else:
                record.last_pain_scale_id = False
                
    @api.depends('neurological_assessment_ids', 'neurological_assessment_ids.date')
    def _compute_last_neurological_assessment(self):
        for record in self:
            if record.neurological_assessment_ids:
                # Ordenar por fecha descendente y tomar la primera
                last_neurological_assessment = record.neurological_assessment_ids.sorted(
                    key=lambda a: a.date, 
                    reverse=True
                )[0]
                record.last_neurological_assessment_id = last_neurological_assessment.id
            else:
                record.last_neurological_assessment_id = False
    
    @api.depends('vital_signs_ids', 'vital_signs_ids.date')
    def _compute_last_vital_signs(self):
        for record in self:
            if record.vital_signs_ids:
                # Ordenar por fecha descendente y tomar la primera
                last_vital_signs = record.vital_signs_ids.sorted(
                    key=lambda a: a.date, 
                    reverse=True
                )[0]
                record.last_vital_signs_id = last_vital_signs.id
            else:
                record.last_vital_signs_id = False
    
    def _update_general_status_check(self):
        """Método que se ejecuta cada 12 horas para revisar el estado general de los residentes"""
        _logger.info("Iniciando revisión automática del estado general de residentes")
        
        try:
            residents = self.search([
                ('active', '=', True),
                ('is_deleted', '=', False)
            ])
            
            _logger.info(f"Encontrados {len(residents)} residentes para revisión")
            
            for resident in residents:
                try:
                    resident._general_status_check()
                except Exception as e:
                    _logger.error(f"Error al procesar residente {resident.id}: {str(e)}")
                    continue
            
            _logger.info("Revisión automática completada exitosamente")
            
        except Exception as e:
            _logger.error(f"Error en _update_general_status_check: {str(e)}")
            raise
    
    def _general_status_check(self):
        """Método que revisa el estado general del residente y crea un registro si existen todas las evaluaciones"""
        self.ensure_one()
        
        _logger.info(f"Iniciando revisión de estado general para residente: {self.name} (ID: {self.id})")
        
        # Lista para almacenar los campos faltantes
        missing_fields = []
        
        # Verificar cada campo last_ individualmente con más información
        field_checks = [
            ('last_anomaly_id', 'anomalía', self.anomaly_ids),
            ('last_pain_scale_id', 'escala de dolor', self.pain_scale_ids),
            ('last_neurological_assessment_id', 'evaluación neurológica', self.neurological_assessment_ids),
            ('last_vital_signs_id', 'signos vitales', self.vital_signs_ids),
        ]
        
        for field_name, field_label, related_records in field_checks:
            field_value = getattr(self, field_name, False)
            
            if not field_value:
                missing_fields.append(field_label)
                
                # Log detallado de por qué falta
                if not related_records:
                    _logger.debug(
                        f"Residente {self.id}: No tiene registros de {field_label} "
                        f"(campo {field_name} está vacío, no hay registros relacionados)"
                    )
                else:
                    # Tiene registros pero no se calculó el last_
                    last_record = related_records.sorted(key=lambda r: r.date, reverse=True)
                    if last_record:
                        _logger.debug(
                            f"Residente {self.id}: Tiene {len(related_records)} registros de {field_label} "
                            f"pero el campo {field_name} no está calculado. "
                            f"El último registro es del {last_record[0].date}"
                        )
        
        # Si faltan campos, registrar en log detallado
        if missing_fields:
            log_message = (
                f"Residente '{self.name}' (ID: {self.id}) no tiene todos los datos para calcular estado general. "
                f"Campos faltantes: {', '.join(missing_fields)}. "
            )
            
            # Añadir información sobre cuántos registros tiene en cada categoría
            log_message += f"Total registros: "
            log_message += f"Anomalías: {len(self.anomaly_ids)}, "
            log_message += f"Escala dolor: {len(self.pain_scale_ids)}, "
            log_message += f"Evaluación neurológica: {len(self.neurological_assessment_ids)}, "
            log_message += f"Signos vitales: {len(self.vital_signs_ids)}"
            
            _logger.warning(log_message)
            general_state_data = {
                'resident_id': self.id,
                'anomaly_id': self.last_anomaly_id.id if self.last_anomaly_id else False,
                'pain_scale_id': self.last_pain_scale_id.id if self.last_pain_scale_id else False,
                'neurological_assessment_id': self.last_neurological_assessment_id.id if self.last_neurological_assessment_id else False,
                'vital_signs_id': self.last_vital_signs_id.id if self.last_vital_signs_id else False,
                'date': fields.Datetime.now(),
            }
            
            # Crear el nuevo registro
            new_record = self.env['medical.resident.state'].sudo().create(general_state_data)
            
            # Forzar el cálculo del estado general inmediatamente
            new_record._compute_general_status()
            return None
        
        _logger.info(
            f"Residente '{self.name}' (ID: {self.id}) tiene todos los datos necesarios. "
            f"Procediendo a crear registro de estado general..."
        )
        
        try:
            # Preparar datos para el nuevo registro
            general_state_data = {
                'resident_id': self.id,
                'anomaly_id': self.last_anomaly_id.id,
                'pain_scale_id': self.last_pain_scale_id.id,
                'neurological_assessment_id': self.last_neurological_assessment_id.id,
                'vital_signs_id': self.last_vital_signs_id.id,
                'date': fields.Datetime.now(),
            }
            
            # Crear el nuevo registro
            new_record = self.env['medical.resident.state'].sudo().create(general_state_data)
            
            # Forzar el cálculo del estado general inmediatamente
            new_record._compute_general_status()
            
            # Log exitoso con detalles
            _logger.info(
                f"✅ Registro de estado general creado exitosamente. "
                f"ID: {new_record.id}, "
                f"Residente: {self.name}, "
                f"Fecha: {new_record.date}, "
                f"Estado: {new_record.general_status} ({new_record.general_status_int})"
            )
            
            return new_record
            
        except ValidationError as ve:
            _logger.error(
                f"❌ Error de validación al crear registro para residente '{self.name}' (ID: {self.id}): {str(ve)}"
            )
            return None
            
        except Exception as e:
            _logger.error(
                f"❌ Error inesperado al crear registro para residente '{self.name}' (ID: {self.id}): {str(e)}",
                exc_info=True  # Esto incluye el traceback completo en el log
            )
            return None