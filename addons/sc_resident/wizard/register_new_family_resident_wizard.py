import re
import logging

from odoo import models, fields, api
from odoo.exceptions import ValidationError, AccessDenied, UserError


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
    family_address = fields.Text(
        string="Dirección",
        required=True,
    )
    kinship_id = fields.Many2one( 'family.kinship', string='Parentesco', required=True)
    is_contractor = fields.Boolean(
        string="Contratante"
    )
    auth_level_ids = fields.Many2many(
        'auth.level', 
        string='Niveles de autorización',
        help="Actividades que el familiar puede realizar con el paciente", 
        required=True,
    )
    
    @api.depends("family_email")
    def _check_valid_family_email(self):
        for record in self:
            if record.family_email:
                # Regex para validar email con dominio correcto
                pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
                if not re.match(pattern, record.family_email):
                    raise ValidationError(
                        "Formato de correo inválido. Debe tener un formato válido como: ejemplo@dominio.com"
                    )

    def action_create_family(self):
        self.ensure_one()
        ResidentFamily = self.env['resident.family'].sudo()
        family = ResidentFamily.create({
            'name': self.family_name,
            'phone': self.family_phone if self.family_phone else False,
            'image_1920' : self.family_image_1920 if self.family_image_1920 else False,
            'email' : self.family_email if self.family_email else False,
            'mobile' : self.family_mobile if self.family_mobile else False,
            'address' : self.family_address if self.family_address else False,   
        })
        
        answer = {} 
        if family:
            RelationshipResidentFamily = self.env['relationship.resident.family'].sudo()
            RelationshipResidentFamily.create({
                'family_id' : family.id,
                'resident_id' : self.current_resident_id.id,
                'kinship_id' : self.kinship_id.id,
                'auth_level_ids' : self.auth_level_ids,
                'is_contractor' : self.is_contractor,
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
