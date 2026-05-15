import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class Resident(models.Model):
    _inherit  = 'resident'

    def action_add_medication(self):
        # Abrir wizard para agregar nuevo medicamento
        return {
            'type': 'ir.actions.act_window',
            'name': f"Crear inventario de medicamento para: {self.name}",
            'res_model': 'medication.inventory.create.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_resident_id': self.id
            }
        }
    
    def action_increase_quantity(self):
        # Obtener los familiares relacionados con este residente
        relationship_records = self.env['relationship.resident.family'].search([
            ('resident_id', '=', self.id)
        ])
        family_ids = relationship_records.mapped('family_id').ids
        
        _logger.info(f"Domain pre:{self.medication_inventory_ids.mapped('id')}")
        return {
            'type': 'ir.actions.act_window',
            'name': f"Incrementar la cantidad de medicamento para: {self.name}",
            'res_model': 'operation.inventory.create.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_resident_id': self.id,
                'default_operation': 'in',
                'default_available_family_ids': [(6, 0, family_ids)]  # Pasar los IDs de familiares
            }
        }
    
    def action_decrease_quantity(self):
        return {
            'type': 'ir.actions.act_window',
            'name': f"Decrementar la cantidad de medicamento para: {self.name}",
            'res_model': 'operation.inventory.create.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_resident_id': self.id,
                'default_operation':'out'
                 
            }
        }
    
    