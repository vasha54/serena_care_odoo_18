import logging
import base64
import os
import re

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class ResidentFamily(models.Model):
    _name = 'resident.family'
    _description = 'Resident Family Model'
    _inherit  = ["soft.delete.mixin", "mail.thread", "mail.activity.mixin"]
    _inherits = {'res.partner': 'partner_id'}

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Contacto',
        required=True,
        ondelete='cascade'
    )
    resident_ids = fields.One2many(
        'relationship.resident.family', 
        'family_id',
        string='Residentes',
    )
    address = fields.Text(
        string="Dirección",
        required=True,
    )
    
    image_with_default = fields.Binary(
        string="Imagen con valor por defecto",
        compute="_compute_image_with_default",
        store=False,
    )

    resident_str = fields.Char(
        string='Residentes Computados',
        compute="_compute_resident_str",
        store=True,
    )
    kinship_str = fields.Char(
        string='Parentesco Computados',
        compute="_compute_kinship_str",
        store=True,
    )
    auth_level_str = fields.Char(
        string='Nivel autorizado Computados',
        compute="_compute_auth_level_str",
        store=True,
    )  
    
    @api.depends("resident_ids")
    def _compute_resident_str(self):
        for record in self:
            names = []
            if record.resident_ids:
                for resident in record.resident_ids:
                    if resident.resident_id:
                        names.append(resident.resident_id.name)
            record.resident_str = ",".join(names)
 
    @api.depends("resident_ids")
    def _compute_kinship_str(self):
        for record in self:
            names = []
            if record.resident_ids:
                for resident in record.resident_ids:
                    if resident.kinship_id:
                        names.append(resident.kinship_id.name)
            record.kinship_str = ",".join(names)

    @api.depends("resident_ids")
    def _compute_auth_level_str(self):
        for record in self:
            names = []
            if record.resident_ids:
                for resident in record.resident_ids:
                    if resident.auth_level_ids:
                        for auth_level in resident.auth_level_ids:
                            names.append(auth_level.name)
            record.auth_level_str = ",".join(names)

    @api.depends("image_1920")
    def _compute_image_with_default(self):
        default_image_path = os.path.join(
            os.path.dirname(__file__), "..", "static", "src", "img", "item_menu_family.png"
        )
        # Leer la imagen por defecto si existe
        default_image = None
        if os.path.exists(default_image_path):
            with open(default_image_path, "rb") as f:
                default_image = base64.b64encode(f.read())

        for record in self:
            if record.image_1920:
                record.image_with_default = record.image_1920
            else:
                record.image_with_default = default_image

    @api.constrains("email")
    def _check_valid_email(self):
        for record in self:
            if record.email:
                # Regex para validar email con dominio correcto
                pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
                if not re.match(pattern, record.email):
                    raise ValidationError(
                        "Formato de correo inválido. Debe tener un formato válido como: ejemplo@dominio.com"
                    )

    @api.model
    def create(self, vals):
        vals['is_company'] = False

        record = super(ResidentFamily, self).create(vals)

        details = _(
            "Se creó el familiar '%(name)s'.\n"
            "Email: %(email)s\n"
            "Teléfono: %(phone)s"
        ) % {
            'name': record.name,
            'email': record.email or 'N/A',
            'phone': record.phone or record.mobile or 'N/A',
        }

        record._create_audit_log('create', details)
        return record

    def unlink(self):
        for record in self:
            # Verificar si este familiar es contratante de algún residente
            contractor_relationships = record.resident_ids.filtered(lambda r: r.is_contractor)
            
            for relationship in contractor_relationships:
                resident = relationship.resident_id
                
                # Buscar otros familiares que sean contratantes del mismo residente
                other_contractors = self.env['relationship.resident.family'].search_count([
                    ('resident_id', '=', resident.id),
                    ('is_contractor', '=', True),
                    ('family_id', '!=', record.id)
                ])
                
                # Si no hay otros contratantes, no permitir la eliminación
                if other_contractors == 0:
                    raise ValidationError(_(
                        "No se puede eliminar el familiar '%(family_name)s' porque es el único contratante "
                        "del residente %(resident_name)s. El residente debe tener al menos un familiar marcado como contratante."
                    ) % {
                        'family_name': record.name,
                        'resident_name': resident.name
                    })
        
        for record in self:
            details = _(
                "Se eliminó el familiar '%(name)s'.\n"
                "Email: %(email)s\n"
                "Teléfono: %(phone)s\n"
                "Residentes asociados: %(residents)s"
            ) % {
                'name': record.name,
                'email': record.email or 'N/A',
                'phone': record.phone or record.mobile or 'N/A',
                'residents': record.resident_str or 'Ninguno',
            }

            record._create_audit_log('unlink', details)

        # Si pasa todas las validaciones, proceder con la eliminación
        # Primero eliminamos las relaciones en RelationshipResidentFamily
        for record in self:
            if record.resident_ids:
                record.resident_ids.unlink()
        
        # Luego eliminamos el propio registro ResidentFamily
        return super(ResidentFamily, self).unlink()
    
    def write(self, vals):
        tracked_fields = ['name', 'email', 'phone', 'mobile','address']
        old_data = {}

        for record in self:
            old_data[record.id] = {
                field: getattr(record, field)
                for field in tracked_fields
            }

        result = super(ResidentFamily, self).write(vals)

        for record in self:
            changes = []

            for field in tracked_fields:
                if field in vals:
                    old = old_data[record.id].get(field)
                    new = getattr(record, field)

                    if old != new:
                        label = dict(self.fields_get()[field]['string'])
                        changes.append(f"{label}: {old or 'N/A'} → {new or 'N/A'}")

            if changes:
                details = _(
                    "Se modificó el familiar '%(name)s':\n%(changes)s"
                ) % {
                    'name': record.name,
                    'changes': "\n".join(changes),
                }

                record._create_audit_log('write', details)

        return result

    def _create_audit_log(self, action_type, details=None):
        AuditLog = self.env['audit.log'].sudo()
        model = self.env['ir.model']._get(self._name)

        for record in self:
            AuditLog.create({
                'name': f"{action_type.capitalize()} familiar",
                'user_id': self.env.user.id,
                'model_id': model.id if model else False,
                'record_id': record.id,
                'action_type': action_type,
                'details': details,
            })
   
