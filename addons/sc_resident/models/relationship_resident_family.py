import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class RelationshipResidentFamily(models.Model):
    _name = 'relationship.resident.family'
    _description = 'Relations Resident-Family Model'

    _sql_constraints = [
        ('unique_resident_family', 
         'UNIQUE(resident_id, family_id)', 
         '¡Ya existe un registro con este residente y familiar! Solo se permite uno por combinación.')
    ]

    auth_level_ids = fields.Many2many(
        'auth.level', 
        string='Niveles de autorización',
        help="Actividades que el familiar puede realizar con el paciente"
    )

    resident_id = fields.Many2one(
        'resident', 
        string='Residente',
        required=True,
        ondelete='cascade'
    )
    family_id = fields.Many2one(
        'resident.family', 
        string='Familiar',
        ondelete='cascade'
    )
    kinship_id = fields.Many2one(
        'family.kinship', 
        string='Parentesco',
        required=True
    )
    is_contractor = fields.Boolean(
        string="Contratante",
    )
    family_name = fields.Char(related='family_id.name', string='Nombre', readonly=False)
    family_phone = fields.Char(related='family_id.phone', string='Teléfono', readonly=False)
    family_mobile = fields.Char(related='family_id.mobile', string='Móvil', readonly=False)
    family_email = fields.Char(related='family_id.email', string='Email', readonly=False) 
    family_image_1920 = fields.Binary(related='family_id.image_1920', string='Foto', readonly=False)
    family_country_id = fields.Many2one(related='family_id.country_id', string='País', readonly=False) 
    family_province_id = fields.Many2one(related='family_id.province_id', string='Provincia', readonly=False) 
    family_municipality_id = fields.Many2one(related='family_id.municipality_id', string='Municipio', readonly=False) 
    family_city = fields.Char(related='family_id.city', string='Ciudad', readonly=False)
    family_zip = fields.Char(related='family_id.zip', string='Código Postal', readonly=False)
    family_street = fields.Char(related='family_id.street', string='Calle principal', readonly=False)
    family_street2 = fields.Char(related='family_id.street2', string='Entre calle #1', readonly=False)
    family_street3 = fields.Char(related='family_id.street3', string='Entre calle #2', readonly=False)
    family_street_number = fields.Char(related='family_id.street_number', string='Número', readonly=False)
    family_address = fields.Text(
        related='family_id.address',    
        string="Dirección",
        readonly=False
    )

    @api.constrains('resident_id', 'family_id')
    def _check_unique_resident_family(self):
        for record in self:
            if not record.resident_id or not record.family_id:
                continue
                
            domain = [
                ('resident_id', '=', record.resident_id.id),
                ('family_id', '=', record.family_id.id),
                ('id', '!=', record.id)
            ]
            
            if self.search_count(domain) > 0:
                raise ValidationError(_(
                    "¡Ya existe una relación entre el residente %(resident)s y el familiar %(family)s! "
                    "No se permiten relaciones duplicadas."
                ) % {
                    'resident': record.resident_id.name,
                    'family': record.family_id.name
                })

    @api.depends('resident_id', 'auth_level_ids', 'kinship_id')
    def _compute_display_name(self):
        for r in self:
            r.display_name = f"{r.resident_id.name} - {r.kinship_id.name} - {r.auth_level_ids.mapped("name")}"

    @api.model
    def create(self, vals):
        record = super(RelationshipResidentFamily, self).create(vals)

        details = _(
            "Se creó la relación entre el residente '%(resident)s' y el familiar '%(family)s'."
        ) % {
            'resident': record.resident_id.name,
            'family': record.family_id.name,
        }

        record._create_audit_log('create', details)
        return record



    def unlink(self):
        for record in self:
            # Check if the record being deleted is a contractor
            if record.is_contractor:
                # Search for other contractors for the same resident
                other_contractors = self.search([
                    ('resident_id', '=', record.resident_id.id),
                    ('is_contractor', '=', True),
                    ('id', '!=', record.id)
                ])
                # If no other contractors are found, prevent deletion
                if not other_contractors :
                    raise ValidationError(_(
                        "No se puede eliminar el registro del contratante '%(record_name)s'. "
                        "El residente %(resident_name)s debe tener al menos un familiar marcado como contratante."
                    ) % {
                        'record_name': record.family_id.name,
                        'resident_name': record.resident_id.name
                    })
        # Proceed with the deletion if validation passes
        for record in self:
            details = _(
                "Se eliminó la relación entre el residente '%(resident)s' y el familiar '%(family)s'. "
                "Parentesco: %(kinship)s."
            ) % {
                'resident': record.resident_id.name,
                'family': record.family_id.name,
                'kinship': record.kinship_id.name,
            }

            record._create_audit_log('unlink', details)
        return super(RelationshipResidentFamily, self).unlink()

    @api.constrains('is_contractor', 'resident_id')
    def _check_at_least_one_contractor(self):
        """
        Ensures a resident always has at least one contractor.
        This constraint triggers when the `is_contractor` field is set to False
        or when the resident_id is changed.
        """
        for record in self:
            if record.is_contractor:
                continue
            other_contractors = self.search_count([
                ('resident_id', '=', record.resident_id.id),
                ('is_contractor', '=', True),
                ('id', '!=', record.id)
            ])
            if other_contractors == 0:
                raise ValidationError(_(
                    "No se puede desmarcar la casilla 'Contratante' para '%(record_name)s'. "
                    "El residente %(resident_name)s debe tener al menos un familiar marcado como contratante."
                ) % {
                    'record_name': record.display_name,
                    'resident_name': record.resident_id.name
                })
    
    def write(self, values):
        if 'is_contractor' in values and not values['is_contractor']:
            for record in self:
                other_contractors = self.search_count([
                    ('resident_id', '=', record.resident_id.id),
                    ('is_contractor', '=', True),
                    ('id', '!=', record.id)
                ])
                if other_contractors == 0:
                    raise ValidationError(_(
                        "No se puede desmarcar la casilla 'Contratante' para '%(record_name)s'. "
                        "El residente %(resident_name)s debe tener al menos un familiar marcado como contratante."
                    ) % {
                        'record_name': record.display_name,
                        'resident_name': record.resident_id.name
                    })
        
        for record in self:
            old_values = {
                'is_contractor': record.is_contractor,
                'kinship': record.kinship_id.name if record.kinship_id else False ,
                'auth_levels': record.auth_level_ids.mapped('name') if record.auth_level_ids else False,
            }
            
        result = super(RelationshipResidentFamily, self).write(values)
        
        for record in self:
            changes = []

            if 'is_contractor' in values:
                changes.append(
                    f"Contratante: {old_values['is_contractor']} → {record.is_contractor}"
                )

            if 'kinship_id' in values:
                changes.append(
                    f"Parentesco: {old_values['kinship']} → {record.kinship_id.name}"
                )

            if 'auth_level_ids' in values:
                changes.append(
                    f"Niveles autorización: {', '.join(old_values['auth_levels'])} → "
                    f"{', '.join(record.auth_level_ids.mapped('name'))}"
                )

            if changes:
                details = _(
                    "Se modificó la relación '%(relation)s':\n%(changes)s"
                ) % {
                    'relation': record.display_name,
                    'changes': "\n".join(changes),
                }

                record._create_audit_log('write', details)
        
        return result
    
    
    def _create_audit_log(self, action_type, details=None):
        AuditLog = self.env['audit.log'].sudo()

        model = self.env['ir.model']._get(self._name)

        for record in self:
            AuditLog.create({
                'name': f"{action_type.capitalize()} relación Residente–Familiar",
                'user_id': self.env.user.id,
                'model_id': model.id if model else False,
                'record_id': record.id,
                'action_type': action_type,
                'details': details,
            })
