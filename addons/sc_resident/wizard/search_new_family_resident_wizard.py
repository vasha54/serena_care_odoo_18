from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class SearchNewFamilyResidentWizard(models.TransientModel):
    _name = 'search.new.family.resident.wizard'
    _description = 'Buscar familiar para asignarselo a un residente'
    
    current_resident_id = fields.Many2one(
        'resident', 
        string="Residente",
        default=lambda self: self.env.context.get('active_id')
    )
    kinship_id = fields.Many2one( 'family.kinship', string='Parentesco', required=True)
    auth_level_ids = fields.Many2many(
        'auth.level', 
        string='Niveles de autorización',
        help="Actividades que el familiar puede realizar con el paciente", 
        required=True,
    )
    family_id = fields.Many2one(
        'resident.family', 
        string='Familiar',
        required=True,
    )
    
    def action_create_family(self):
        self.ensure_one()
        RelationshipResidentFamily = self.env['relationship.resident.family'].sudo()
        exist_relation = RelationshipResidentFamily.search_count([
                            ('family_id','=',self.family_id.id),
                            ('resident_id','=',self.current_resident_id.id)
                        ])
        answer  = {}
        if exist_relation > 0:
            answer = {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                                'message': f'Ya la persona {self.family_id.name} está registrada como familiar del residente {self.current_resident_id.name}',
                                'type': 'warning',
                                'next': {'type': 'ir.actions.act_window_close'},
                            }
                    }
        else:
            RelationshipResidentFamily.create({
                'family_id' : self.family_id.id,
                'resident_id' : self.current_resident_id.id,
                'kinship_id' : self.kinship_id.id,
                'auth_level_ids' : self.auth_level_ids,  
            })
            answer = {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                                'message': f'Se asigno correctamente el familiar al residente {self.current_resident_id.name}',
                                'type': 'success',
                                'next': {'type': 'ir.actions.act_window_close'},
                            }
                    } 
        
        return answer
