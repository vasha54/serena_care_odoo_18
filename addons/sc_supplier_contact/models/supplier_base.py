import logging

from odoo import models, fields, api, _, tools
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class SupplierBase(models.Model):
    _name = "supplier.base"
    _description = "Modelo base del contacto del proveedor"
    _inherit = ["soft.delete.mixin", "mail.thread", "mail.activity.mixin"]
    _inherits = {"res.partner": "partner_id"}

    partner_id = fields.Many2one(
        comodel_name="res.partner", string="Contacto", required=True, ondelete="cascade"
    )
    provider_type = fields.Selection(
        [
            ("hospital", "Hospital"),
            ("clinic", "Clínica"),
            ("laboratory", "Laboratorio"),
            ("specialist", "Especialista"),
            ("doctor", "Médico"),
        ],
        string="Tipo de Proveedor",
        required=True,
    )
    nomenclature_specialty_id = fields.Many2one(
        string="Especialidad",
        comodel_name="nomenclature.specialty.supplier",
        ondelete="restrict",
        domain=[("active", "=", True)],
    )
    works_at_id = fields.Many2one(
        'res.partner',
        string="Trabaja en",
        related='partner_id.parent_id',
        readonly=False,
        domain="[('is_supplier_sc', '=', True),('is_company','=',True),('active','=',True)]"
    )


    @api.constrains('provider_type', 'nomenclature_specialty_id')
    def _check_specialty_required(self):
        for record in self:
            if record.provider_type in ['doctor', 'specialist'] and not record.nomenclature_specialty_id:
                raise ValidationError(_("La especialidad es obligatoria para proveedores tipo Doctor o Especialista"))

    @api.model
    def create(self, vals):
        # Validar especialidad para doctor/specialist
        if vals.get('provider_type') in ['doctor', 'specialist'] and not vals.get('nomenclature_specialty_id'):
            raise ValidationError(_("La especialidad es obligatoria para proveedores tipo Doctor o Especialista"))
        
        # Configurar is_company en el partner
        if vals.get('provider_type') in ['hospital', 'clinic', 'laboratory']:
            vals['is_company'] = True
        else:
            vals['is_company'] = False
        
        # Crear el partner primero con los valores adecuados
        vals.update({
            'is_supplier_sc': True,
            'parent_id': vals.get('parent_id'),  # Mantener el parent_id si se proporciona
        })
        # partner = self.env['res.partner'].create(partner_vals)
        # vals['partner_id'] = partner.id

        # Crear el registro de supplier.base
        record = super(SupplierBase, self).create(vals)

        # Auditoría: crear registro en audit.log
        self.env['audit.log'].sudo().create({
            'name': f"Creación de proveedor {record.name or 'Nuevo'}",
            'user_id': self.env.user.id,
            'model_id': self.env['ir.model']._get_id('supplier.base'),
            'record_id': record.id,
            'action_type': 'create',
            'details': f"Valores creados: {vals}",
        })

        return record

    def write(self, vals):
        # Validar especialidad para doctor/specialist
        for record in self:
            new_provider_type = vals.get('provider_type', record.provider_type)
            current_specialty = record.nomenclature_specialty_id
            
            # Si estamos cambiando a doctor/specialist sin especificar especialidad
            if new_provider_type in ['doctor', 'specialist']:
                new_specialty = vals.get('nomenclature_specialty_id', current_specialty.id if current_specialty else False)
                if not new_specialty:
                    raise ValidationError(_("La especialidad es obligatoria para proveedores tipo Doctor o Especialista"))
            
            # Si estamos cambiando de doctor/specialist a otro tipo, quitar especialidad
            elif record.provider_type in ['doctor', 'specialist'] and new_provider_type not in ['doctor', 'specialist']:
                vals['nomenclature_specialty_id'] = False

        # Configurar is_company en el partner relacionado
        if 'provider_type' in vals:
            partner_vals = {}
            if vals['provider_type'] in ['hospital', 'clinic', 'laboratory']:
                vals['is_company'] = True
                vals['works_at_id'] = False
            else:
                vals['is_company'] = False
            # # Actualizar el partner
            # self.partner_id.write(partner_vals)

        # Capturar cambios antiguos para auditoría
        old_values = {
            record.id: {
                field: getattr(record, field) for field in vals.keys() if hasattr(record, field)
            } for record in self
        }

        # Escribir los cambios
        result = super(SupplierBase, self).write(vals)

        # Auditoría: crear registro en audit.log para cada registro modificado
        for record in self:
            changes = []
            for field in vals.keys():
                if hasattr(record, field):
                    old_val = old_values[record.id].get(field)
                    new_val = getattr(record, field)
                    if old_val != new_val:
                        changes.append(f"{field}: {old_val} -> {new_val}")
            
            if changes:
                self.env['audit.log'].sudo().create({
                    'name': f"Modificación de proveedor {record.name}",
                    'user_id': self.env.user.id,
                    'model_id': self.env['ir.model']._get_id('supplier.base'),
                    'record_id': record.id,
                    'action_type': 'write',
                    'details': "Cambios: " + "; ".join(changes),
                })

        return result

    def unlink(self):
        # Auditoría: crear registro en audit.log antes de eliminar
        for record in self:
            self.env['audit.log'].sudo().create({
                'name': f"Eliminación de proveedor {record.name}",
                'user_id': self.env.user.id,
                'model_id': self.env['ir.model']._get_id('supplier.base'),
                'record_id': record.id,
                'action_type': 'unlink',
                'details': f"Registro eliminado: {record.name} (ID: {record.id})",
            })
        return self.action_soft_delete()
        
        

    