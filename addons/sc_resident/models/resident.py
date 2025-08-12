import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class Resident(models.Model):
    _name = 'resident'
    _description = 'Resident Model'
    _inherit  = ['soft.delete.mixin']
    _inherits = {'res.partner': 'partner_id'}

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Contacto',
        required=True,
        ondelete='cascade'
    )
    sex_id = fields.Many2one(
        comodel_name='res.sex',
        string='Sexo',
        required=True,
        help='Sexo a la que pertenece el residente',
    )
    residence_id = fields.Many2one(
        comodel_name='residence_house',
        string='Residencia',
        required=True,
        help='Residencia a la que pertenece el residente',
        domain="[('active', '=', True)]"
    )
    birth_date = fields.Date(
        string='Fecha de Nacimiento',
        required=True,
        help='Fecha de nacimiento del residente'
    )
    country_id = fields.Many2one(
        comodel_name='res.country',
        string='País',
        default=lambda self: self.env.ref('base.mx',False),
        help='País de origen del residente'
    )

    _sql_constraints = [
        ('name_resident_unique', 'UNIQUE(name)', 'El nombre del residente debe ser único!'),
    ]

    def unlink(self):
        if not self.active:
           raise UserError(f"No se puede eliminar el residente {self.name} por estar inactivo")

        model_id = self.env['ir.model']._get('resident').id
        AuditLog = self.env['audit.log'].sudo()
        AuditLog.create({
            'name': f"Se eliminó el residente {self.name}",
            'user_id': self.env.user.id,
            'model_id': model_id,
            'record_id': self.id,
            'action_type': 'unlink',
            'details': f"El residente se encontraba en la residencia {self.residence_id.name} en" 
                    " el momento que fue eliminado del sistema"
        })
        return self.action_soft_delete()

    @api.model
    def create(self, vals):
        if vals.get('name'):
            self._check_unique_name(vals['name'])
        return super().create(vals)

    def write(self, vals):

        if not vals.get('active'):
            for record in self:
               if not record.active:
                    raise UserError(f"No se puede modificar el residente {record.name} por estar inactivo")

        if vals.get('name'):
            for record in self:
                self._check_unique_name(vals['name'], record.id)
        return super().write(vals)


    def _check_unique_name(self, name, exclude_id=None):
        domain = [('name', '=', name)]
        if exclude_id:
            domain.append(('id', '!=', exclude_id))
        if self.search_count(domain) > 0:
            raise ValidationError("El nombre del residente debe ser único!")
