import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class MedicalMedication(models.Model):
    _inherit = "medical.medication"

    inventory_id = fields.Many2one(
        string='Inventario asociado', 
        comodel_name='medication.inventory', ondelete='restrict')

    @api.model
    def create(self, values):
        # Crear el registro de MedicalMedication
        result = super().create(values)
        
        # Obtener los valores necesarios para la búsqueda
        resident_id = result.resident_id.id
        medicament_id = result.medicament_id.id
        pharmaceutical_form = result.pharmaceutical_form
        uom = result.dosage_unit
        uom_id = uom.id
        cat_uom_id = uom.category_id.id
        
        # Acceder al modelo MedicationInventory
        MedicationInventory = self.env['medication.inventory'].sudo()
        
        # Buscar el registro existente en MedicationInventory
        inventory_record = MedicationInventory.search([
            ('resident_id', '=', resident_id),
            ('medicament_id', '=', medicament_id),
            ('pharmaceutical_form', '=', pharmaceutical_form),
            ('cat_uom_id', '=', cat_uom_id)
        ], limit=1)
        
        # Si no existe, crear un nuevo registro en MedicationInventory
        if not inventory_record:
            inventory_record = MedicationInventory.create({
                'medicament_id': medicament_id,
                'pharmaceutical_form': pharmaceutical_form,
                'resident_id': resident_id,
                'available_quantity': 0,
                'alert_quantity': 0,
                'warning_quantity': 0,
                'uom_id': uom_id,
                'cat_uom_id': cat_uom_id,
            })
        
        # Agregar el registro de MedicalMedication al campo medical_indication_ids
        inventory_record.write({
            'medical_indication_ids': [(4, result.id)]
        })
        inventory_record._compute_reason_inventory()
        result.write({'inventory_id':inventory_record.id})
        return result
