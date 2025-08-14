import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class RelationshipResidentFamily(models.Model):
    _name = 'relationship.resident.family'
    _description = 'Relations Resident-Family Model'

    _sql_constraints = [
        ('unique_resident_family', 
         'UNIQUE(resident_id, family_id)', 
         '¡Ya existe un registro con este residente y familiar! Solo se permite uno por combinación.')
    ]

    auth_level_ids = fields.Many2many(
        'auth.level', 
        string='Niveles de autorización',
        help="Actividades que el familiar puede realizar con el paciente"
    )

    resident_id = fields.Many2one(
        'resident', 
        string='Residente',
        required=True,
        ondelete='cascade'
    )
    family_id = fields.Many2one(
        'resident.family', 
        string='Familiar',
        ondelete='cascade'
    )
    kinship_id = fields.Many2one(
        'family.kinship', 
        string='Parentesco',
        required=True
    )
    family_name = fields.Char(related='family_id.name', string='Nombre', readonly=False)
    family_phone = fields.Char(related='family_id.phone', string='Teléfono', readonly=False)
    family_mobile = fields.Char(related='family_id.mobile', string='Móvil', readonly=False)
    family_email = fields.Char(related='family_id.email', string='Email', readonly=False) 
    family_image_1920 = fields.Binary(related='family_id.image_1920', string='Foto', readonly=False)
    family_country_id = fields.Many2one(related='family_id.country_id', string='País', readonly=False) 
    family_province_id = fields.Many2one(related='family_id.province_id', string='Provincia', readonly=False) 
    family_municipality_id = fields.Many2one(related='family_id.municipality_id', string='Municipio', readonly=False) 
    family_city = fields.Char(related='family_id.city', string='Ciudad', readonly=False)
    family_zip = fields.Char(related='family_id.zip', string='Código Postal', readonly=False)
    family_street = fields.Char(related='family_id.street', string='Calle principal', readonly=False)
    family_street2 = fields.Char(related='family_id.street2', string='Entre calle #1', readonly=False)
    family_street3 = fields.Char(related='family_id.street3', string='Entre calle #2', readonly=False)
    family_street_number = fields.Char(related='family_id.street_number', string='Número', readonly=False)
    
    @api.constrains('resident_id', 'family_id')
    def _check_unique_resident_family(self):
        for record in self:
            if not record.resident_id or not record.family_id:
                continue
                
            domain = [
                ('resident_id', '=', record.resident_id.id),
                ('family_id', '=', record.family_id.id),
                ('id', '!=', record.id)
            ]
            
            if self.search_count(domain) > 0:
                raise ValidationError(_(
                    "¡Ya existe una relación entre el residente %(resident)s y el familiar %(family)s! "
                    "No se permiten relaciones duplicadas."
                ) % {
                    'resident': record.resident_id.name,
                    'family': record.family_id.name
                }) 

    
