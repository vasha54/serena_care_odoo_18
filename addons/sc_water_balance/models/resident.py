import logging
import json 

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class Resident(models.Model):
    _inherit = "resident"


    water_balance_ids = fields.One2many(
        "water.balance.annotation",
        "resident_id",
        string="Registros del balance hídrico",
        help="Listado del balance hídrico del residente",
    )
    total_water_balance =  fields.Float(
        string="Total del balance hídrico",
        compute="_compute_water_balance",
        store=True,
        digits=(3,1)
    )
    status_water_balance = fields.Selection(
        [
            ("unknow", "Sin registros"), 
            ("neutro", "Neutro"), 
            ("positive", "Positivo"),
            ("negative", "Negativo"),
        ],
        string="Estado del balance hídrico",
        compute="_compute_water_balance",
        store=True,
    )
    status_water_balance_label = fields.Char(
        string='Estado del balance hídrico',
        compute='_compute_water_balance',
        store=False
    )
    
            
    @api.depends('water_balance_ids')
    def _compute_water_balance(self):
        for record in self:
            record.status_water_balance = 'unknow'
            record.total_water_balance = 0
            if record.water_balance_ids:
                accumalated = 0
                for register in record.water_balance_ids:
                    if  register.type_annotation == 'income':
                        accumalated = accumalated + register.quantity
                    else:
                        accumalated = accumalated - register.quantity
                record.total_water_balance = accumalated
                if accumalated > 0.000:
                   record.status_water_balance = 'positive'
                elif accumalated < 0.000:
                   record.status_water_balance = 'negative'
                else:
                   record.status_water_balance = 'neutro'
            record.status_water_balance_label = dict(
                self._fields['status_water_balance'].selection
            ).get(record.status_water_balance, '') 

    # Campos para las gráficas
    # water_balance_income_data = fields.Text(
    #     compute='_compute_water_balance_chart_data',
    #     string='Datos para gráfica de ingresos'
    # )
    # water_balance_expense_data = fields.Text(
    #     compute='_compute_water_balance_chart_data',
    #     string='Datos para gráfica de egresos'
    # )
    # water_balance_timeline_data = fields.Text(
    #     compute='_compute_water_balance_timeline_data',
    #     string='Datos para gráfica de timeline'
    # )
    #
    # @api.depends('water_balance_ids')
    # def _compute_water_balance_chart_data(self):
    #     """Calcula los datos para las gráficas circulares de ingresos y egresos por vía"""
    #     for record in self:
    #         income_data = {}
    #         expense_data = {}
    #
    #         for balance in record.water_balance_ids:
    #             route_name = balance.route_id.name or 'Sin vía'
    #             if balance.type_annotation == 'income':
    #                 income_data[route_name] = income_data.get(route_name, 0) + balance.quantity
    #             else:
    #                 expense_data[route_name] = expense_data.get(route_name, 0) + balance.quantity
    #
    #         # Convertir a formato JSON para las gráficas
    #         record.water_balance_income_data = json.dumps([
    #             {'name': name, 'value': value}
    #             for name, value in income_data.items()
    #         ])
    #         record.water_balance_expense_data = json.dumps([
    #             {'name': name, 'value': value}
    #             for name, value in expense_data.items()
    #         ])
    #
    #
    # @api.depends('water_balance_ids')
    # def _compute_water_balance_timeline_data(self):
    #     """Calcula los datos para la gráfica de timeline por día"""
    #     for record in self:
    #         daily_data = {}
    #
    #         for balance in record.water_balance_ids:
    #             # Usar la fecha sin la hora para agrupar por día
    #             date_str = balance.create_date.strftime('%Y-%m-%d') if balance.create_date else 'Sin fecha'
    #
    #             if date_str not in daily_data:
    #                 daily_data[date_str] = {'income': 0, 'expense': 0}
    #
    #             if balance.type_annotation == 'income':
    #                 daily_data[date_str]['income'] += balance.quantity
    #             else:
    #                 daily_data[date_str]['expense'] += balance.quantity
    #
    #         # Ordenar por fecha y convertir a formato para la gráfica
    #         sorted_dates = sorted(daily_data.keys())
    #         timeline_data = []
    #
    #         for date_str in sorted_dates:
    #             data = daily_data[date_str]
    #             timeline_data.append({
    #                 'date': date_str,
    #                 'income': data['income'],
    #                 'expense': -data['expense'],  # Egresos como valores negativos
    #                 'balance': data['income'] - data['expense']
    #             })
    #
    #         record.water_balance_timeline_data = json.dumps(timeline_data)
    #

    
    # @api.depends('water_balance_ids', 'water_balance_ids.quantity',
    #              'water_balance_ids.route_id', 'water_balance_ids.type_annotation')
    # def _compute_water_balance_chart_data(self):
    #     for record in self:
    #         if not record.water_balance_ids:
    #             record.water_balance_chart_data = False
    #             continue
    #
    #         # Agrupar datos por route_id y type_annotation
    #         data_dict = {}
    #         for balance in record.water_balance_ids:
    #             if balance.route_id:
    #                 route_name = balance.route_id.name
    #                 type_annotation = balance.type_annotation
    #                 key = f"{route_name} ({type_annotation})"
    #
    #                 if key not in data_dict:
    #                     data_dict[key] = 0
    #                 data_dict[key] += balance.quantity
    #
    #         # Convertir a formato para el gráfico
    #         chart_data = []
    #         for label, value in data_dict.items():
    #             chart_data.append({
    #                 'label': label,
    #                 'value': value
    #             })
    #
    #         record.water_balance_chart_data = json.dumps({
    #             'data': chart_data,
    #             'title': 'Balance Hídrico por Vía y Tipo'
    #         })
    #
    # water_balance_chart_data = fields.Text(
    #     compute='_compute_water_balance_chart_data',
    #     string='Datos del Gráfico',
    #     store=False
    # )
