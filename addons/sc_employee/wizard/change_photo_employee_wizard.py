from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class ChangePhotoEmployeeWizard(models.TransientModel):
    _name = 'change.photo.employee.wizard'
    _description = 'Wizard para cambiar la foto del empleado'
    
    current_employee_id = fields.Many2one(
        'hr.employee', 
        string="Empleado",
        default=lambda self: self.env.context.get('default_current_employee_id')
    )
    current_image_1920 = fields.Binary(
        related='current_employee_id.image_1920', 
        string='Foto', 
        readonly=True)
    
    new_image_1920 = fields.Binary(
        string='Nueva Foto', 
        required=True,)

    
    def action_change_photo_employee(self):
        self.ensure_one() 
        self.current_employee_id.write({'image_1920':self.new_image_1920})
        return {
            'type':'ir.actions.client',
             'tag':'reload',
        }
        
        
        
        