import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError
from datetime import date, timedelta
from collections import defaultdict

_logger = logging.getLogger(__name__)


class Resident(models.Model):
    _inherit  = 'resident'

    assessment_ids = fields.One2many(
        'mood.assessment', 
        'resident_id',
        string='Evaluaciones de ánimo',
        help="Listado de las evaluaciones de ánimo vinculadas al residente"
    )
    
    def get_assessment_moods_between_dates(self, date_start, date_end):
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

        return self.env['mood.assessment'].search(domain)
    
    def get_predominant_mood_between_dates(self, date_start, date_end):
        """
        Retorna el estado de ánimo predominante del residente en las evaluaciones
        realizadas entre date_start y date_end (ambos inclusive).
        En caso de empate en frecuencia, se selecciona el estado con la evaluación
        más reciente (última aparición por fecha).
        :param date_start: fecha de inicio (objeto date)
        :param date_end:   fecha de fin (objeto date)
        :return: record de mood.state o None si no hay evaluaciones
        """
        self.ensure_one()

        # Validar fechas (opcional, pero recomendado)
        if not date_start or not date_end:
            return None

        # Ajustar fecha fin para cubrir todo el día final
        date_end_adj = date_end + timedelta(days=1)

        # Filtrar evaluaciones del residente en el rango
        assessments = self.assessment_ids.filtered_domain([
            ('date', '>=', date_start),
            ('date', '<', date_end_adj)
        ])

        if not assessments:
            return None

        # Diccionarios para contar frecuencias y guardar última fecha por estado
        freq = defaultdict(int)
        last_date = {}

        for ass in assessments:
            state = ass.mood_state_id
            if state:  # Ignorar evaluaciones sin estado (aunque deberían tenerlo)
                freq[state] += 1
                # Actualizar última fecha si corresponde
                if state not in last_date or ass.date > last_date[state]:
                    last_date[state] = ass.date

        if not freq:
            return None

        # Encontrar la frecuencia máxima
        max_count = max(freq.values())

        # Filtrar estados con frecuencia máxima
        candidates = [state for state, count in freq.items() if count == max_count]
        return candidates

        # if len(candidates) == 1:
        #     return candidates[0]

        # # Si hay empate, ordenar por fecha más reciente (descendente) y tomar el primero
        # candidates_sorted = sorted(candidates, key=lambda s: last_date[s], reverse=True)
        # return candidates_sorted[0]