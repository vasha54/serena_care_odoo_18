import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import timedelta
_logger = logging.getLogger(__name__)

class ResidentFamilyReportWizard(models.TransientModel):
    _name = 'resident.family.report.wizard'
    _description = 'Wizard para informe de familiares'

    resident_id = fields.Many2one(
        'resident',
        string='Residente',
        required=True,
        default=lambda self: self.env.context.get('active_id')
    )
    date_end = fields.Date(
        string='Fecha de fin',
        required=True,
        default=lambda self: fields.Date.context_today(self)
    )
    date_start = fields.Date(
        string='Fecha inicio',
        required=True,
        default=lambda self: fields.Date.context_today(self) - timedelta(days=7) 
    )
    notes = fields.Text(string='Observaciones / Notas')

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for record in self:
            if record.date_start and record.date_end:
                if record.date_start > record.date_end:
                    raise ValidationError(_('La fecha de inicio debe ser anterior o igual a la fecha de fin.'))
                delta = record.date_end - record.date_start
                if delta.days > 7:
                    raise ValidationError(_('La diferencia entre fechas no puede ser mayor a 7 días.'))
            
    def _convert_nutrition_to_dict(self, _nutritions):
        """
        Convierte un recordset de nutriciones (nutrition)
        en una lista de diccionarios con los datos necesarios para el reporte.
        :param activities: recordset de nutrition
        :return: list of dict
        """
        self.ensure_one()  # Opcional, asegura que se llama desde un solo residente
        result = []
        for act in _nutritions:
            # Formatear fecha con zona horaria del usuario
            date_formatted = ''
            if act.date_user:
                date_formatted = act.date_user.strftime('%d/%m/%Y %H:%M')

            result.append({
                'date': date_formatted,
                'level': act.nutrition_level_id.name if act.nutrition_level_id else '',
                'user': act.user_id.name if act.user_id else '',
                'description': act.description or '',
            })
        return result
    
    def _convert_mood_to_dict(self, _moods):
        """
        Convierte un recordset de actividades (resident.recreation.activity.rel)
        en una lista de diccionarios con los datos necesarios para el reporte.
        :param activities: recordset de resident.recreation.activity.rel
        :return: list of dict
        """
        self.ensure_one()  # Opcional, asegura que se llama desde un solo residente
        result = []
        for act in _moods:
            # Formatear fecha con zona horaria del usuario
            date_formatted = ''
            if act.date_user:
                date_formatted = act.date_user.strftime('%d/%m/%Y %H:%M')

            # Manejar la imagen de forma segura
            state_image = ''
            if act.mood_state_id and act.mood_state_id.image:
                try:
                    state_image = act.mood_state_id.image.decode('utf-8')
                except (UnicodeDecodeError, AttributeError):
                    # Si hay error, se deja vacío (podrías loguearlo)
                    pass

            result.append({
                'date': date_formatted,
                'state_name': act.mood_state_id.name if act.mood_state_id else '',
                'state_image': state_image,
                'user': act.user_id.name if act.user_id else '',
                'observations_clinic': act.observations_clinic or '',
            })
        return result
                
    def _convert_activity_to_dict(self, _activities):
        """
        Convierte un recordset de actividades (resident.recreation.activity.rel)
        en una lista de diccionarios con los datos necesarios para el reporte.
        :param activities: recordset de resident.recreation.activity.rel
        :return: list of dict
        """
        self.ensure_one()  # Opcional, asegura que se llama desde un solo residente
        result = []
        for act in _activities:
            # Formatear fecha con zona horaria del usuario
            date_formatted = ''
            if act.date_execution_user:
                date_formatted = act.date_execution_user.strftime('%d/%m/%Y %H:%M')

            # Manejar la imagen de forma segura
            type_image = ''
            if act.activity_type_id and act.activity_type_id.image_with_default:
                try:
                    type_image = act.activity_type_id.image_with_default.decode('utf-8')
                except (UnicodeDecodeError, AttributeError):
                    # Si hay error, se deja vacío (podrías loguearlo)
                    pass

            result.append({
                'date': date_formatted,
                'type_name': act.activity_type_id.name if act.activity_type_id else '',
                'type_image': type_image,
                'user': act.user_id.name if act.user_id else '',
                'description': act.description or '',
            })
        return result

    def action_print_report(self):
        self.ensure_one()
        # Validación explícita antes de generar el reporte
        if self.date_start > self.date_end:
            raise UserError(_('La fecha de inicio debe ser anterior o igual a la fecha de fin.'))
        delta = self.date_end - self.date_start
        if delta.days > 7:
            raise UserError(_('La diferencia entre fechas no puede ser mayor a 7 días.'))

        # Datos comunes a todos los reportes
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        date_server = fields.Datetime.now()
        date_user = self.resident_id._convert_timezone(self.env.user, date_server)
        activitys_recreations = self.resident_id.get_activities_between_dates(self.date_start,self.date_end)
        assessment_moods = self.resident_id.get_assessment_moods_between_dates(self.date_start,self.date_end)
        predominant_mood = self.resident_id.get_predominant_mood_between_dates(self.date_start,self.date_end)
        assessment_nutritions = self.resident_id.get_assessment_nutritions_between_dates(self.date_start,self.date_end)
        nutrition_averages = self.resident_id.get_daily_nutrition_average(self.date_start,self.date_end)
        
        activitys_data = self._convert_activity_to_dict(activitys_recreations)
        nutritions_data = self._convert_nutrition_to_dict(assessment_nutritions)
        moods_data = self._convert_mood_to_dict(assessment_moods)
        predominant_mood_data = None
        if predominant_mood:
            predominant_mood_data = []
            for r in predominant_mood:
                predominant_mood_data.append(
                    {
                        'name': r.name,
                        'image': r.image.decode('utf-8')
                    }
                )
            
        _logger.info(f'Fechas {self.date_start} - {self.date_end}')

        # Llamar al informe
        report_action = self.env.ref('sc_reports.report_resident_family_pdf').with_context(
            close_on_report_download=True,
            website_url=base_url,
            date_user=date_user,
            wizard_date_start=self.date_start,
            wizard_date_end=self.date_end,
            wizard_notes=self.notes,
            wizard_activitys_recreations = activitys_data,
            wizard_assessment_moods = moods_data,
            wizard_predominant_mood = predominant_mood_data,
            wizard_nutrition_averages = nutrition_averages,
            wizard_assessment_nutritions = nutritions_data,
        ).report_action(self.resident_id, config=False)
        
        # 👇 Esto fuerza el cierre del wizard en OWL
        report_action.update({
            'close_on_report_download': True,
        })

        return report_action