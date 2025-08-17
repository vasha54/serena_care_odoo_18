from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

import logging
import re

_logger = logging.getLogger(__name__)

class MedicamentComposition(models.Model):
    _name = 'medicament.composition'
    _description = 'Composición del Medicamento'
    
    medicament_id = fields.Many2one(
        'medicament.product', 
        string='Medicamento',
        required=True,
        ondelete='cascade'
    )
    substance_id = fields.Many2one(
        'medicament.substance', 
        string='Sustancia (Activo o Excipientes)',
        required=True,
        ondelete='restrict',  
    )
    quantity = fields.Float(string='Cantidad', required=True)
    unit_measure = fields.Selection(
        selection=[
            ('mg', 'miligramos (mg)'),
            ('g', 'gramos (g)'),
            ('ml', 'mililitros (ml)'),
            ('%', 'porcentaje (%)'),
            ('ui', 'Unidades Internacionales (UI)'),
            ('mcg', 'microgramos (mcg)'),  # Hormonas tiroideas, vitamina B12
            ('mmol', 'milimoles (mmol)'),   # Electrolitos como potasio
            ('mg/g', 'miligramos por gramo (mg/g)'),  # Cremas y ungüentos
            ('ui/g', 'UI por gramo (UI/g)'), # Pomadas oftálmicas
            ('mg/ml', 'miligramos por mililitro (mg/ml)'), # Soluciones inyectables
            ('mg/m2', 'miligramos por metro cuadrado (mg/m²)'), # Quimioterapéuticos
            ('ui/ml', 'UI por mililitro (UI/ml)'), # Insulina, heparina
            ('ppm', 'partes por millón (ppm)'), # Soluciones desinfectantes
            ('l', 'litros (L)'),             # Soluciones de irrigación
        ],
        string='Unidad de Medida',
        required=True
    )
 
    @api.constrains('unit_measure', 'quantity')
    def _check_values_composition(self):
        for items in self:
            if items.unit_measure == '%' and (items.quantity < 0 or items.quantity > 100):
                raise ValidationError("El porcentaje debe estar entre 0 y 100")
            elif items.quantity <= 0:
                raise ValidationError("La cantidad debe ser mayor que cero")

    @api.constrains('medicament_id', 'substance_id')
    def _check_unique_substance(self):
        for items in self:
            if self.search_count([
                ('medicament_id', '=', items.medicament_id.id),
                ('substance_id', '=', items.substance_id.id),
                ('id', '!=', items.id)
            ]) > 0:
                raise ValidationError("¡Cada sustancia solo puede aparecer una vez por medicamento!")

    @api.constrains('substance_id')
    def _check_substance_in_use(self):
        for rec in self:
            if rec.substance_id and not rec.substance_id.active:
                raise ValidationError(
                    "El activo/excipiente %s está desactivado y no puede usarse" % rec.substance_id.name
                )
