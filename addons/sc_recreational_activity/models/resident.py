import logging

from dateutil.relativedelta import relativedelta
from datetime import date, timedelta

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class Resident(models.Model):
    _inherit  = 'resident'

    activitys_recreations_ids = fields.One2many(
        'resident.recreation.activity.rel', 
        'resident_id',
        string='Actividades',
        help="Listado de las actividades en la que el residente ha partipado",
    )
    
    # Campo computado para actividades de los últimos 7 días
    last_7_days_activities = fields.One2many(
        'resident.recreation.activity.rel',
        'resident_id',
        string='Actividades (Últimos 7 días)',
        compute='_compute_last_7_days_activities',
        store=False,  # No se almacena en BD porque se calcula dinámicamente
        help="Actividades realizadas por el residente en los últimos 7 días",
    )
    
    # Campo para contar actividades de los últimos 7 días
    last_7_days_activities_count = fields.Integer(
        string='Nº Actividades (Últimos 7 días)',
        compute='_compute_last_7_days_activities',
        store=True,
        help="Número de actividades realizadas en los últimos 7 días",
    )
    
    @api.depends('activitys_recreations_ids.date_execution')
    def _compute_last_7_days_activities(self):
        """Calcula las actividades de los últimos 7 días y su conteo"""
        for resident in self:
            # Obtener fecha límite (hace 7 días desde hoy)
            seven_days_ago = date.today() - relativedelta(days=7)
            
            # Filtrar actividades de los últimos 7 días
            recent_activities = resident.activitys_recreations_ids.filtered(
                lambda activity: activity.date_execution and 
                activity.date_execution.date() >= seven_days_ago
            )
            
            # Asignar las actividades filtradas
            resident.last_7_days_activities = recent_activities
            
            # Contar las actividades
            resident.last_7_days_activities_count = len(recent_activities)
            
    def get_activities_between_dates(self, date_start, date_end):
        """
        Retorna las actividades recreativas del residente realizadas entre
        date_start y date_end, incluyendo ambos extremos.
        :param date_start: fecha de inicio (objeto date)
        :param date_end:   fecha de fin (objeto date)
        :return: recordset de resident.recreation.activity.rel
        """
        self.ensure_one()  # Asegura que se llama sobre un solo residente

        # Ajustamos la fecha fin para incluir todo el día final
        # (date_execution es datetime, por eso usamos < date_end + 1 día)
        date_end_adj = date_end + timedelta(days=1)

        domain = [
            ('resident_id', '=', self.id),
            ('date_execution', '>=', date_start),
            ('date_execution', '<', date_end_adj)
        ]

        return self.env['resident.recreation.activity.rel'].search(domain)
    
    
