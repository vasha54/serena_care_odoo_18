from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class RegisterNewFamilyResidentWizard(models.TransientModel):
    _name = 'register.new.family.resident.wizard'
    _description = 'Registrar un nuevo familiar para asignarselo a un residente'
    
    current_resident_id = fields.Many2one(
        'resident', 
        string="Residente",
        default=lambda self: self.env.context.get('active_id')
    )
    family_name = fields.Char( string='Nombre', required=True)
    family_phone = fields.Char( string='Teléfono')
    family_mobile = fields.Char( string='Móvil', required=True)
    family_email = fields.Char( string='Email', required=True) 
    family_image_1920 = fields.Binary( string='Foto')
    family_country_id = fields.Many2one( 'res.country',string='País') 
    family_province_id = fields.Many2one('res_province_mx' ,string='Provincia') 
    family_municipality_id = fields.Many2one('res_municipality_mx' ,string='Municipio') 
    family_city = fields.Char( string='Ciudad')
    family_zip = fields.Char( string='Código Postal')
    family_street = fields.Char( string='Calle principal')
    family_street2 = fields.Char( string='Entre calle #1')
    family_street3 = fields.Char( string='Entre calle #2')
    family_street_number = fields.Char( string='Número')
    kinship_id = fields.Many2one( 'family.kinship', string='Parentesco', required=True)
    auth_level_ids = fields.Many2many(
        'auth.level', 
        string='Niveles de autorización',
        help="Actividades que el familiar puede realizar con el paciente", 
        required=True,
    )
    
    

    def action_create_family(self):
        self.ensure_one()
        ResidentFamily = self.env['resident.family'].sudo()
        family = ResidentFamily.create({
            'name': self.family_name,
            'phone': self.family_phone if self.family_phone else False,
            'country_id': self.family_country_id if self.family_country_id else False,
            'image_1920' : self.family_image_1920 if self.family_image_1920 else False,
            'city' : self.family_city if self.family_city else False,
            'email' : self.family_email if self.family_email else False,
            'mobile' : self.family_mobile if self.family_mobile else False,
            'municipality_id' : self.family_municipality_id if self.family_municipality_id else False,
            'province_id' : self.family_province_id if self.family_province_id else False,
            'zip' : self.family_zip if self.family_zip else False,
            'street' : self.family_street if self.family_street else False,
            'street2' : self.family_street2 if self.family_street2 else False,
            'street3' : self.family_street3 if self.family_street3 else False,
            'street_number' : self.family_street_number if self.family_street_number else False,   
        })
        
        answer = {} 
        if family:
            RelationshipResidentFamily = self.env['relationship.resident.family'].sudo()
            RelationshipResidentFamily.create({
                'family_id' : family.id,
                'resident_id' : self.current_resident_id.id,
                'kinship_id' : self.kinship_id.id,
                'auth_level_ids' : self.auth_level_ids,  
            }) 
            answer = {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                                'message': f'Se creo y asigno correctamente el familiar al residente {self.current_resident_id.name}',
                                'type': 'success',
                                'next': {'type': 'ir.actions.act_window_close'},
                            }
                    }
        else:
            answer = {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                                'message': f'No se pudo crear y asignar correctamente el familiar al residente {self.current_resident_id.name}',
                                'type': 'error',
                                'next': {'type': 'ir.actions.act_window_close'},
                            }
                    }
        
        return answer
