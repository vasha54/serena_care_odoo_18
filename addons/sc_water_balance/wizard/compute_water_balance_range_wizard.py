import logging
from datetime import datetime, timedelta

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)


class ComputeWaterBalanceRangeWizard(models.TransientModel):
    _name = "compute.water.balance.range.wizard"
    _description = "Wizard para calcular el balance hídrico de un paciente en un rango de fecha"
    
    resident_id = fields.Many2one(
        "resident",
        string="Residente",
        required=True,
        ondelete="restrict",
        default=lambda self: self.env.context.get("active_id"),
    )
    
    # Campo para seleccionar el tipo de intervalo
    interval_type = fields.Selection(
        [
            ('day', 'Día (últimas 24 horas)'),
            ('week', 'Semana (últimos 7 días)'),
            ('month', 'Mes (últimos 30 días)'),
            ('custom', 'Rango personalizado'),
        ],
        string="Tipo de intervalo",
        default='day',
        required=True,
    )
    
    start_date_range = fields.Datetime(
        string="Desde",
        required=False
    )
    end_date_range = fields.Datetime(
        string="Hasta",
        required=False,
        default=lambda self: fields.Datetime.now()
    )
    
    # Campos computados
    annotation_ids = fields.One2many(
        'water.balance.annotation',
        compute='_compute_annotations',
        string='Registros encontrados'
    )
    
    annotation_count = fields.Integer(
        compute='_compute_annotations',
        string='Total de registros'
    )
    
    total_income = fields.Float(
        compute='_compute_annotations',
        string='Total Ingresos (ml)'
    )
    
    total_expense = fields.Float(
        compute='_compute_annotations',
        string='Total Egresos (ml)'
    )
    
    balance = fields.Float(
        compute='_compute_annotations',
        string='Balance (ml)'
    )
    
    status_water_balance = fields.Selection(
        [
            ("unknow", "Sin registros"), 
            ("neutro", "Neutro"), 
            ("positive", "Positivo"),
            ("negative", "Negativo"),
        ],
        string="Estado del balance hídrico",
        compute="_compute_annotations",
        store=False,
    )
    
    @api.onchange('interval_type')
    def _onchange_interval_type(self):
        """Calcula automáticamente las fechas según el tipo de intervalo seleccionado"""
        for wizard in self:
            end_date = fields.Datetime.now()
            start_date = fields.Datetime.now()
            wizard.annotation_ids = False
            if wizard.interval_type != 'custom':
                if wizard.interval_type == 'day':
                    # Últimas 24 horas
                    start_date = end_date - timedelta(days=1)
                elif wizard.interval_type == 'week':
                    # Últimos 7 días
                    start_date = end_date - timedelta(days=7)
                elif wizard.interval_type == 'month':
                    # Últimos 30 días
                    start_date = end_date - timedelta(days=30)
                
            wizard.start_date_range = start_date
            wizard.end_date_range = end_date
                
                
    
    @api.constrains('start_date_range', 'end_date_range')
    def _check_dates(self):
        for record in self:
            if record.start_date_range and record.end_date_range:
                if record.start_date_range > record.end_date_range:
                    raise ValidationError(_("La fecha de inicio debe ser anterior o igual a la fecha de fin."))

    @api.depends('start_date_range', 'end_date_range', 'interval_type')
    def _compute_annotations(self):
        for wizard in self:
            if wizard.start_date_range and wizard.end_date_range:
                # Si no es personalizado, recalcular las fechas
                if wizard.interval_type != 'custom':
                    wizard._onchange_interval_type()
                
                # Buscar registros en el rango de fechas
                domain = [
                    ('resident_id', '=', wizard.resident_id.id),
                    ('date', '>=', wizard.start_date_range),
                    ('date', '<=', wizard.end_date_range)
                ]
                
                annotations = self.env['water.balance.annotation'].search(domain)
                wizard.annotation_ids = annotations
                wizard.annotation_count = len(annotations)
                
                # Calcular totales
                wizard.total_income = sum(
                    annotation.quantity 
                    for annotation in annotations 
                    if annotation.type_annotation == 'income'
                )
                
                wizard.total_expense = sum(
                    annotation.quantity 
                    for annotation in annotations 
                    if annotation.type_annotation == 'expense'
                )
                
                wizard.balance = wizard.total_income - wizard.total_expense
                
                # Determinar estado
                if wizard.annotation_count == 0:
                    wizard.status_water_balance = 'unknow'
                elif wizard.balance > 0.000:
                    wizard.status_water_balance = 'positive'
                elif wizard.balance < 0.000:
                    wizard.status_water_balance = 'negative'
                else:  
                    wizard.status_water_balance = 'neutro'
            else:
                wizard.annotation_ids = False
                wizard.annotation_count = 0
                wizard.total_income = 0
                wizard.total_expense = 0
                wizard.balance = 0
                wizard.status_water_balance = 'unknow'

    def action_compute_water_balance(self):
        """Acción para calcular el balance hídrico"""
        self.ensure_one()
        
        # Si no es personalizado, recalcular las fechas antes de computar
        if self.interval_type != 'custom':
            self._onchange_interval_type()
        
        # Forzar el recálculo de los campos computados
        self._compute_annotations()
        
        return {
            "name": f"Calcular balance hídrico del residente: {self.resident_id.name}",
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': self._context,
        }