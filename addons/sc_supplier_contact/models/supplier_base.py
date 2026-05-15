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
            ("other", "Otro"),
        ],
        string="Tipo de Proveedor",
        defaults='other',      
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
    is_affiliate = fields.Boolean(string = "Afiliado", default=False)
    discount = fields.Char(string = "Descuento")
    category_id = fields.Many2one(
        'supplier.category',
        string='Categoría de Proveedor',
        
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
        records = super(SupplierBase, self).create(vals)

        # Crear log de auditoría para cada registro creado
        for record in records:
            self.env['audit.log'].sudo().crud_audit_log(record, 'supplier.base', 'create')
        return records


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

        # Guardar estado anterior para detectar cambios (opcional, mejora la calidad del detalle)
        old_values = {}
        for record in self:
            old_values[record.id] = {
                field: record[field] for field in vals if field in record._fields and not record._fields[field].compute
            }
        result = super().write(vals)
        # Después de la escritura, crear logs con los campos modificados
        for record in self:
            changed_fields = []
            for field, new_val in vals.items():
                if field in old_values.get(record.id, {}):
                    old_val = old_values[record.id][field]
                    if old_val != record[field]:
                        changed_fields.append(f"{field}: {old_val!r} -> {record[field]!r}")
                else:
                    # Campo no almacenado o no presente en el registro anterior, se registra igual
                    changed_fields.append(f"{field}: {record[field]!r}")
            if changed_fields:
                details = "Campos modificados: " + "; ".join(changed_fields)
            else:
                details = "Modificación sin cambios detectados"
            self.env['audit.log'].sudo().crud_audit_log(record, 'supplier.base', 'write', extra_details=details)
        return result

    def unlink(self):
        # Auditoría: crear registro en audit.log antes de eliminar
        for record in self:
            self.env['audit.log'].sudo().crud_audit_log(record, 'supplier.base', 'unlink')
        return self.action_soft_delete()
        
        

    