from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class ResSex(models.Model):
    _name = 'res.sex'
    _description = 'Sexo'
    _order = 'name asc'

    name = fields.Char(
        string='Nombre', 
        required=True,
        index=True,
        help="Nombre completo del sexo (ej: Masculino, Femenino)")
    
    acronym = fields.Char(
        string='Abreviatura', 
        required=True,
        size=5,
        help="Abreviatura en mayúsculas (ej: M, F)")

    _sql_constraints = [
        ('acronym_sex_unique', 'UNIQUE(acronym)', 'La abreviatura debe ser única!'),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._valid_name(vals.get('name'))
            vals['acronym'] = self._normalizar_acronym(vals.get('acronym'))
        return super().create(vals_list)

    def write(self, vals):
        if 'name' in vals:
            self._valid_name(vals['name'])
        if 'acronym' in vals:
            vals['acronym'] = self._normalizar_acronym(vals['acronym'])
        return super().write(vals)

    def _normalizar_acronym(self, abrev):
        """Convierte la abreviatura a mayúsculas y elimina espacios"""
        if abrev:
            return abrev.strip().upper()
        return abrev

    def _valid_name(self, nombre):
        """Valida que el nombre sea único (case-insensitive)"""
        if not nombre:
            return
        
        nombre_normalizado = nombre.strip().lower()
        
        existente = self.search([
            ('id', '!=', self.id if self else False),
            ('name', '=ilike', nombre_normalizado)
        ], limit=1)
        
        if existente:
            raise ValidationError(_(
                "Ya existe un sexo con el nombre '%s' (ignorando mayúsculas/minúsculas).",
                nombre_normalizado
            ))

    @api.constrains('name')
    def _check_name_unique(self):
        for record in self:
            record._valid_name(record.name)

    @api.constrains('acronym')
    def _check_acronym(self):
        for record in self:
            if not record.acronym.isupper():
                raise ValidationError(_(
                    "La abreviatura debe estar en MAYÚSCULAS: %s",
                    record.acronym
                ))