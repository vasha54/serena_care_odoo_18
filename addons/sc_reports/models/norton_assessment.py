import re

from dateutil.relativedelta import relativedelta
from datetime import datetime
from pytz import timezone

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError

import logging
_logger = logging.getLogger(__name__)

class NortonAssessment(models.Model):
    _inherit = 'norton.assessment'
    
    date_user = fields.Datetime(
        string='Fecha para el usuario',
        compute='_compute_date_user', 
        store=False,
    )
    physical_condition_label = fields.Char(
        string='Estado Físico',
        compute='_compute_physical_condition_label',
        store=False
    )
    mental_state_label = fields.Char(
        string='Estado Mental',
        compute='_compute_mental_state_label',
        store=False
    )
    activity_label = fields.Char(
        string='Actividad',
        compute='_compute_activity_label',
        store=False
    )
    mobility_label = fields.Char(
        string='Movibilidad',
        compute='_compute_mobility_label',
        store=False
    )
    incontinence_label = fields.Char(
        string='Incontinencia',
        compute='_compute_incontinence_label',
        store=False
    )
    risk_level_label = fields.Char(
        string='Nivel de Riesgo',
        compute='_compute_risk_level_label',
        store=False
    )
    
    @api.depends('physical_condition')
    def _compute_physical_condition_label(self):
        for record in self:
            record.physical_condition_label = dict(
                self._fields['physical_condition'].selection
            ).get(record.physical_condition, '') 
            
    @api.depends('mental_state')
    def _compute_mental_state_label(self):
        for record in self:
            record.mental_state_label = dict(
                self._fields['mental_state'].selection
            ).get(record.mental_state, '') 
            
    @api.depends('activity')
    def _compute_activity_label(self):
        for record in self:
            record.activity_label = dict(
                self._fields['activity'].selection
            ).get(record.activity, '') 
    
    @api.depends('mobility')
    def _compute_mobility_label(self):
        for record in self:
            record.mobility_label = dict(
                self._fields['mobility'].selection
            ).get(record.mobility, '') 
            
    @api.depends('incontinence')
    def _compute_incontinence_label(self):
        for record in self:
            record.incontinence_label = dict(
                self._fields['incontinence'].selection
            ).get(record.incontinence, '') 
            
    @api.depends('risk_level')
    def _compute_risk_level_label(self):
        for record in self:
            record.risk_level_label = dict(
                self._fields['risk_level'].selection
            ).get(record.risk_level, '') 
    
    @api.depends('date')
    def _compute_date_user(self):
        user = self.env.user
        for r in self:
            if user and r.date:
                r.date_user = r._convert_timezone(user,r.date) 
                
    def _convert_timezone(self, _user, _date):
        """
        Convierte un datetime de UTC a la zona horaria del usuario.
        
        Args:
            _user: objeto usuario con tz
            _date: objeto datetime (asume que está en UTC)
        """
        _logger.info(f"User tz: {_user.tz}")
        user_tz = timezone(_user.tz or 'UTC')
        utc_tz = timezone('UTC')
        
        # Asegurarnos de que el datetime tenga zona horaria UTC
        if _date.tzinfo is None:
            # Si es naive, asumir que está en UTC y añadir timezone UTC
            utc_dt = utc_tz.localize(_date)
        else:
            # Si ya tiene timezone, convertir a UTC por si acaso
            utc_dt = _date.astimezone(utc_tz)
        
        # Convertir a la zona del usuario
        user_dt = utc_dt.astimezone(user_tz)
        
        return user_dt.strftime('%Y-%m-%d %H:%M:%S')
           