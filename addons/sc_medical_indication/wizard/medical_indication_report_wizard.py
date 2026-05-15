import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)

class MedicalIndicationReportWizard(models.TransientModel):
    _name = 'medical.indication.report.wizard'
    _description = 'Wizard para reporte de indicaciones médicas'

    resident_id = fields.Many2one(
        'resident', 
        string='Residente',
        required=True,
        default=lambda self: self._get_default_resident()
    )
    quantity = fields.Integer(
        string='Cantidad de Indicaciones',
        required=True,
        default=10,
        help='Número de indicaciones médicas a incluir en el reporte'
    )

    def _get_default_resident(self):
        # Obtener el residente del contexto
        return self.env.context.get('active_id')

    def generate_report(self):
        # Validar que la cantidad sea positiva
        if self.quantity <= 0:
            raise UserError(_('La cantidad debe ser un número positivo.'))
        
        # Obtener las indicaciones ordenadas por fecha descendente
        indications = self.env['unified.medical.indication'].search([
            ('resident_id', '=', self.resident_id.id)
        ], order='create_date desc', limit=self.quantity)
        
        if not indications:
            raise UserError(_('No hay indicaciones médicas para este residente.'))
        
        # Preparar datos para el reporte - FORMA CORRECTA
        indications_data = []
        selection_dict = dict(self.env['unified.medical.indication']._fields['indication_type'].selection)
        for ind in indications:
            indication_type_label = selection_dict.get(ind.indication_type, '')
            indications_data.append({
                'create_date': ind.create_date.strftime('%Y-%m-%d %H:%M') if ind.create_date else '',
                'doctor': ind.user_id.name or '',
                'type': indication_type_label,
                'note': ind.note or 'Sin detalles',  # Asegúrate de que este campo existe
            })
        
        data = {
            'resident_name': self.resident_id.name,
            'quantity': min(self.quantity,len(indications_data)),
            'indications': indications_data,
        }
        
        # Retornar acción para generar el reporte - FORMA CORRECTA
        return {
            'type': 'ir.actions.report',
            'report_name': 'sc_medical_indication.report_medical_indication_template',
            'report_type': 'qweb-pdf',
            'data': data,
            'context': self.env.context,
        }