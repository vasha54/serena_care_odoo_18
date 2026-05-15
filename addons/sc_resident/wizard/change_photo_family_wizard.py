from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class ChangePhotoFamilyWizard(models.TransientModel):
    _name = 'change.photo.family.wizard'
    _description = 'Wizard para cambiar la foto del familiar'
    
    current_family_id = fields.Many2one(
        'resident.family', 
        string="Familiar",
        default=lambda self: self.env.context.get('default_current_family_id')
    )
    current_image_1920 = fields.Binary(
        related='current_family_id.image_1920', 
        string='Foto', 
        readonly=True)
    
    new_image_1920 = fields.Binary(
        string='Nueva Foto', 
        required=True,)

    
    def action_change_photo_family(self):
        self.ensure_one() 
        self.current_family_id.write({'image_1920':self.new_image_1920})
        return {
            'type':'ir.actions.client',
             'tag':'reload',
        }
        
        
        
        