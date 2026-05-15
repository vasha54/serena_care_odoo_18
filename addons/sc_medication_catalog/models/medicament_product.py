from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

import logging
import re

_logger = logging.getLogger(__name__)

class Product(models.Model):

    _inherit = 'product.template'

    is_medicament = fields.Boolean(
        string="Es medicamento",
        default=False,
        help="Saber si el producto es un medicamento es un medicamento o no")

class MedicamentProduct(models.Model):
    _name = 'medicament.product'
    _description = "Producto Medicamento"
    _inherits = {'product.template':'product_id'}

    # _sql_constraints = [
    #     ('code_medicament_unique', 'UNIQUE(code)', 'La clave debe ser única para cada medicamento!'),
    # ]

    product_id = fields.Many2one(
        'product.template',
        string="Plantilla de producto",
        required=True,
        ondelete='cascade',
    )
    brand_commercial = fields.Char(
        string='Marca comercial',
    )
     
    code = fields.Char(string="Clave", )
    category = fields.Char(string="Grupo", )
    pharmaceutical_form = fields.Char(string="Forma Farmacéutica", required=True)
    # pharmaceutical_form_id = fields.Many2one(
    #     'pharmaceutical.form', 
    #     string='Forma Farmacéutica', 
    #     required=True, 
    #     ondelete='restrict',
    # )
    composicion = fields.Text(string='Composición')
    # composicion_ids = fields.One2many(
    #     'medicament.composition', 
    #     'medicament_id', 
    #     string='Composición',
    #     required=True,
    # )
    dosage = fields.Text(string='Dosis por Grupo Poblacional')
    # dosage_ids = fields.One2many(
    #     'medicament.dosage',
    #     'medicament_id',
    #     string='Dosis por Grupo Poblacional',
    #     required=True
    # )
    others_details_presentation = fields.Text(string="Otros detalles de la presentación")
    indications = fields.Text(string="Indicaciones")

    @api.depends('name','brand_commercial','code')
    def _compute_display_name(self):
        for record in self:
            name = getattr(record, 'name', '') or ''
            brand = getattr(record, 'brand_commercial', '') or ''
            code = getattr(record, 'code', '') or ''
            parts = []
            if name:
                parts.append(name)
            if brand:
                parts.append(f"({brand})")
            if code:
                parts.append(f"/ {code}")
            record.display_name = ' '.join(parts) if parts else f"Nuevo medicamento"


    @api.model
    def create(self, vals):
        self._validate_code(vals.get('code'))
        vals.update({
                        'is_medicament': True,
                    })
        records = super().create(vals)
        # Crear log de auditoría para cada registro creado
        for record in records:
            self.env['audit.log'].sudo().crud_audit_log(record, 'medicament.product', 'create')
        return records

    def write(self, vals):
        
        if 'code' in vals:
            self._validate_code(vals['code'], self.id)
        vals.update({'is_medicament': True})
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
            self.env['audit.log'].sudo().crud_audit_log(record, 'medicament.product', 'write', extra_details=details)
        return result
    
    def unlink(self):
        # Antes de eliminar, crear logs para cada registro
        for record in self:
            self.env['audit.log'].sudo().crud_audit_log(record, 'medicament.product', 'unlink')
        return super().unlink() 

    def _validate_dosage_fields(self, vals):
        if bool(vals.get('children_route_admin_id')) != bool(vals.get('children_dosage')):
            raise ValidationError(
                "Los campos 'Vía de administración para niños' y 'Dosis para niños' "
                "deben ambos tener valor o ambos estar vacíos."
            )
        
        if bool(vals.get('adult_route_admin_id')) != bool(vals.get('adult_dosage')):
            raise ValidationError(
                "Los campos 'Vía de administración para adultos' y 'Dosis para adultos' "
                "deben ambos tener valor o ambos estar vacíos."
            )

    @api.constrains('code')
    def _check_code_format(self):
        for record in self:
            if record.code and len(record.code) > 0:
                record._validate_code(record.code)

    def _validate_code(self, code, medicament_id=-100):
        """Valida el formato del código: XXX.XXX.XXXX.XX"""
        pattern = r'^\d{3}\.\d{3}\.\d{4}\.\d{2}$'
        if code and len(code) > 0 and not re.match(pattern, code):
            raise ValidationError(
                "El código debe tener el formato: XXX.XXX.XXXX.XX "
                "(donde X es un dígito numérico). Ejemplo: 123.456.7890.12"
            )

    # @api.constrains('pharmaceutical_form_id')
    # def _check_pharmaceutical_form_in_use(self):
    #     for rec in self:
    #         if rec.pharmaceutical_form_id and not rec.pharmaceutical_form_id.active:
    #             raise ValidationError(
    #                 "La forma de presentación %s está desactivado y no puede usarse" % rec.pharmaceutical_form_id.name
    #             )

    


