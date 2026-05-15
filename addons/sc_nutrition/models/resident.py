import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError
from datetime import date, timedelta
from collections import defaultdict

_logger = logging.getLogger(__name__)


class Resident(models.Model):
    _inherit  = 'resident'

    nutrition_ids = fields.One2many(
        'nutrition', 
        'resident_id',
        string='Alimentación',
        help="Listado de las alimentaciones vinculadas al residente"
    )
    
    def get_assessment_nutritions_between_dates(self, date_start, date_end):
        """
        Retorna las evaluaciones de animo del residente realizadas entre
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
            ('date', '>=', date_start),
            ('date', '<', date_end_adj)
        ]

        return self.env['nutrition'].search(domain)
    
    def get_daily_nutrition_average(self, date_start, date_end):
        """
        Calcula el promedio diario del porcentaje de alimentación del residente
        entre date_start y date_end (ambos inclusive).
        :param date_start: fecha de inicio (objeto date)
        :param date_end:   fecha de fin (objeto date)
        :return: lista de diccionarios [{'date': fecha, 'average_percent': float}, ...]
                 ordenada por fecha ascendente. Si no hay registros, retorna lista vacía.
        """
        self.ensure_one()

        # Validar fechas (opcional)
        if not date_start or not date_end:
            return []

        # Ajustar fecha fin para incluir todo el día final
        date_end_adj = date_end + timedelta(days=1)

        # Filtrar nutriciones del residente en el rango
        nutritions = self.nutrition_ids.filtered_domain([
            ('date', '>=', date_start),
            ('date', '<', date_end_adj)
        ])

        if not nutritions:
            return []

        # Agrupar porcentajes por día
        daily_data = defaultdict(list)
        for nut in nutritions:
            # Extraer la fecha (sin hora) del datetime
            day = nut.date.date()
            # Obtener el porcentaje del nivel de alimentación (si existe)
            percent = nut.nutrition_level_id.percent if nut.nutrition_level_id else 0.0
            daily_data[day].append(percent)

        # Calcular promedio por día y ordenar cronológicamente
        result = []
        for day in sorted(daily_data.keys()):
            avg = sum(daily_data[day]) / len(daily_data[day])
            # Opcional: redondear a 2 decimales
            avg = round(avg, 2)
            result.append({
                'date': day,
                'average_percent': avg
            })

        return result
