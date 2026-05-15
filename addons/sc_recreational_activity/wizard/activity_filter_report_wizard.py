import logging
import re
import os
import base64
import json
from dateutil.relativedelta import relativedelta
from datetime import date

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class ActivityFilterReportWizard(models.TransientModel):
    _name = 'activity.filter.report.wizard'
    _description = 'Wizard para reporte de actividades recreativas'

    resident_id = fields.Many2one(
        "resident",
        string="Residente",
        required=True,
        ondelete="restrict",
        default=lambda self: self.env.context.get("active_id"),
    )

    activity_type_ids = fields.Many2many(
        'nomenclature.activity.type',
        string='Tipos de Actividad',
        relation='activity_type_report_wizard_rel',
    )
    all_activity_type = fields.Boolean(string="Todo tipo de actividad", default=False)
    date_start = fields.Datetime(
        string='Fecha Inicio',
        required=True
    )
    date_end = fields.Datetime(
        string='Fecha Fin',
        required=True
    )
    report_type = fields.Selection(
        [
            ('pdf', 'PDF'),
            ('excel', 'Excel')
        ],
        string='Tipo de Reporte',
        default=lambda self: self.env.context.get('format_report'),
        required=True
    )

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for record in self:
            if record.date_start and record.date_end:
                if record.date_start > record.date_end:
                    raise UserError(_('La fecha de inicio no puede ser mayor a la fecha fin'))

    def generate_report(self):
        self.ensure_one()
        
        # Validar fechas
        if self.date_start > self.date_end:
            raise UserError(_('La fecha de inicio no puede ser mayor a la fecha fin'))
        
        # Filtrar actividades
        domain = [
            ('activity_type_id', 'in', self.activity_type_ids.ids),
            ('date_execution', '>=', self.date_start),
            ('date_execution', '<=', self.date_end),
            ('resident_id', '=', self.resident_id.id)
        ]
        if self.all_activity_type:
            domain= domain[1:]
        
        activities = self.env['resident.recreation.activity.rel'].search(domain)
        
        if not activities:
            raise UserError(_('No se encontraron actividades con los criterios seleccionados'))
    
        # Generar reporte según el tipo seleccionado
        if self.report_type == 'pdf':
            # Preparar datos para el reporte
            report_data = self._prepare_report_data(activities)
            return self._generate_pdf_report(report_data)
        else:
            record_ids = activities.ids
            return self._generate_excel_report(record_ids)

    def _prepare_report_data(self, activities):
        """Preparar datos estructurados para el reporte"""
        data = []
        
        for activity in activities:
            activity_data = {
                'activity_name': activity.activity_type_id.name,
                'date_execution': activity.date_execution,
                'description': activity.description,
                'registered_by': activity.user_id.name,
                'resident': activity.resident_id.name,
            }
            
            data.append(activity_data)
        
        return {
            'activities': data,
            'date_start': self.date_start,
            'date_end': self.date_end,
            'activity_types': self.activity_type_ids.mapped('name'),
            'generation_date': fields.Datetime.now()
        }

    def _generate_pdf_report(self, data):
        """Generar reporte en PDF"""
        return {
            'type': 'ir.actions.report',
            'report_name': 'sc_recreational_activity.recreational_activity_pdf_report_resident',
            'report_type': 'qweb-pdf',
            'data': data,
            'context': self.env.context
        }

    def _generate_excel_report(self, _ids):
        """Generar reporte en Excel"""
        return {
            "type": "ir.actions.act_url",
            "url": "/recreational_activity/excel_report_resident/%s" % json.dumps(_ids),
            "target": "new",
        }