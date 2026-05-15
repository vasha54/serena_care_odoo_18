from  odoo import _, api, fields, models

class SoftEditMixin(models.AbstractModel):
    _name = 'soft.edit.mixin'

    is_edit = fields.Boolean(
        string="Editado",
        default=False,
        index=True,
    )

    def action_soft_edit(self):
        self.write({'is_edit':True})
        return {
            'type':'ir.actions.client',
             'tag':'reload',
        }

    
    
    
