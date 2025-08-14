from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class FamilyKinship(models.Model):
    _name = 'family.kinship'
    _description = 'Relación de parentesco familiar'
    _order = 'name'
    _rec_name = 'name'

    name = fields.Char(
        string='Parentesco',
        required=True,
        index=True,
        help='Nombre de la relación de parentesco (por ejemplo, Padre, Madre)'
    )
    description = fields.Text(
        string='Descripción',
        help='Explicación detallada de la relación'
    )
    inverse_relation = fields.Char(
        string='Relación inversa',
        help='La relación opuesta (por ejemplo, Hijo por Padre)'
    )
    degree = fields.Selection(
        [('direct', 'Directa'),
         ('extended', 'Extendida'),
         ('in_law', 'Consuegro'),
         ('other', 'Otro')],
        string='Grado de parentesco',
        default='direct'
    )

    _sql_constraints = [
        ('name_uniq_kinship', 'UNIQUE (name)', 
         '¡Ya existe un parentesco con este nombre!'),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'name' in vals:
                vals['name'] = vals['name'].strip().lower()
        return super().create(vals_list)

    def write(self, vals):
        if 'name' in vals:
            vals['name'] = vals['name'].strip().lower()
        return super().write(vals)

    @api.constrains('name')
    def _check_name(self):
        for rec in self:
            existing = self.search([
                ('name', '=ilike', rec.name),
                ('id', '!=', rec.id)
            ], limit=1)
            if existing:
                raise ValidationError(
                    f"¡Ya existe una relación de parentesco llamada '{rec.name}'!"
                )