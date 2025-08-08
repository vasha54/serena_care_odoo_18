from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)

class MedicamentCategory(models.Model):
    _name = 'medicament.category'
    _description = "Grupo de medicamento"
    _inherits = {'product.category':'category_id'}

    category_id = fields.Many2one(
        'product.category',
        string = "Categoría Padre",
        required = True,
        ondelete = 'cascade',
    )
    is_medicament_category = fields.Boolean(
        string="Es categoría de medicamentos",
        default=True,
    ) 
    
    @api.model 
    def create(self, vals):
        vals['is_medicament_category'] = True
        return super().create(vals)