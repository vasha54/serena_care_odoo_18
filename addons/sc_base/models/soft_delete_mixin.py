from  odoo import _, api, fields, models

class SoftDeleteMixin(models.AbstractModel):
    _name = 'soft.delete.mixin'

    is_deleted = fields.Boolean(
        string="Eliminado",
        default=False,
        index=True,
    )

    def action_soft_delete(self):
        self.write({'is_deleted':True})
        return {
            'type':'ir.actions.client',
             'tag':'reload',
        }

    def action_restore(self):
        self.write({'is_deleted':False})
        return {
            'type':'ir.actions.client',
             'tag':'reload',
        }
