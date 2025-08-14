from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

import logging
import re

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit ='product.template'
    
    is_medicament = fields.Boolean(
        string = "Es un medicamento",
        default = True,
    )
    medicament_product_ids = fields.One2many(
        'medicament.product', 
        'product_tmp_id',
        string = "Detalles de Medicamento")
    categ_id = fields.Many2one(
        "product.category",
        string = "Grupo de medicamento",
        domain = "[('is_medicament_category','=',True)]",
        required = True,      
    )

    def fields_get(self, allfields=None, attributes=None):
        res = super().fields_get(allfields, attributes)
        if 'is_medicament' in res:
            res['is_medicament']['searchable'] = False 
        return res


class MedicamentProduct(models.Model):
    _name = 'medicament.product'
    _description = "Producto Medicamento"
    _inherits = {'product.template':'product_tmp_id'}

    _sql_constraints = [
        ('code_medicament_unique', 'UNIQUE(code)', 'La clave debe ser única para cada medicamento!'),
    ]

    product_tmp_id = fields.Many2one(
        'product.template',
        string="Plantilla de producto",
        required=True,
        ondelete='cascade',
    )
    code = fields.Char(string="Clave", required=True)
    pharmaceutical_form_id = fields.Many2one(
        'pharmaceutical.form', 
        string='Forma Farmacéutica', 
        required=True, 
        ondelete='restrict'
    )
    composition = fields.Text(string="Composición", required=True)
    indications = fields.Text(string="Indicaciones", required=True)
    route_dosage = fields.Text(string="Vía de administración y Dosis", required=True)
    # adult_dosage = fields.Text(string="Dosis para adultos")
    # children_dosage = fields.Text(string="Dosis para niños")
    # adult_route_admin_id = fields.Many2one(
    #     'route.administration',
    #     string='Vía de administración para adultos', 
    #     ondelete='restrict'
    # )
    # children_route_admin_id = fields.Many2one(
    #     'route.administration',
    #     string='Vía de administración para niños', 
    #     ondelete='restrict'
    # )

    
    @api.model
    def create(self, vals):
        #self._validate_dosage_fields(vals)
        self._validate_code(vals.get('code'))
        vals.update({'is_medicament': True})
        return super().create(vals)

    def write(self, vals):
        # for record in self:
        #     combined_vals = {
        #         'children_route_admin_id': vals.get('children_route_admin_id', record.children_route_admin_id.id),
        #         'children_dosage': vals.get('children_dosage', record.children_dosage),
        #         'adult_route_admin_id': vals.get('adult_route_admin_id', record.adult_route_admin_id.id),
        #         'adult_dosage': vals.get('adult_dosage', record.adult_dosage),
        #     }
        #     self._validate_dosage_fields(combined_vals)
        if 'code' in vals:
            self._validate_code(vals['code'], self.id)
        vals.update({'is_medicament': True})
        return super().write(vals)  

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
            if record.code:
                record._validate_code(record.code)

    def _validate_code(self, code, medicament_id=-100):
        """Valida el formato del código: XXX.XXX.XXXX.XX"""
        pattern = r'^\d{3}\.\d{3}\.\d{4}\.\d{2}$'
        if not re.match(pattern, code):
            raise ValidationError(
                "El código debe tener el formato: XXX.XXX.XXXX.XX "
                "(donde X es un dígito numérico). Ejemplo: 123.456.7890.12"
            )

    


