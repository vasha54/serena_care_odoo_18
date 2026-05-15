import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class MedicationInventoryCreateWizard(models.TransientModel):
    _name = 'medication.inventory.create.wizard'
    _description = 'Crear el inventario de un medicamento para un residente desde la vista del residente que no responde a ninguna indicación médica de tipo medicamento'

    resident_id = fields.Many2one(
        'resident', 
        string='Residente',
        required=True,
        default=lambda self: self._get_default_resident()
    )

    medicament_id = fields.Many2one(
        "medicament.product", string="Medicamento", required=True
    )
    pharmaceutical_form = fields.Char(
        related='medicament_id.pharmaceutical_form',
        readonly=True,
        string='Forma Farmacéutica', 
        required=True, 
        ondelete='restrict',
        tracking=True
    )
    alert_quantity = fields.Float(
        string="Cantidad de Notificación de Alerta", required=True
    )
    warning_quantity = fields.Float(
        string="Cantidad de Notificación de Advertencia", required=True
    )
    uom_id = fields.Many2one("uom.uom", string="Unidad de Medida", required=True)
    reason_inventory = fields.Text(
        string="Motivo de la existencia de este inventario",
        required=True,
    )
    init_quantity = fields.Float(
        string="Cantidad de inicial", required=True
    )
    family_id = fields.Many2one(
        'resident.family', 
        string='Familiar que provee cantidad inicial',
        domain="[('id', 'in', available_family_ids)]"
    )
    available_family_ids = fields.Many2many(
        'resident.family',
        compute='_compute_available_family_ids',
        string='Familiares disponibles'
    )
    
    @api.depends('resident_id')
    def _compute_available_family_ids(self):
        for wizard in self:
            if wizard.resident_id:
                relationships = self.env['relationship.resident.family'].sudo().search([
                    ('resident_id', '=', wizard.resident_id.id)
                ])
                wizard.available_family_ids = relationships.mapped('family_id')
            else:
                wizard.available_family_ids = False


    def _get_default_resident(self):
        # Obtener el residente del contexto
        return self.env.context.get('default_resident_id')

    @api.constrains('init_quantity')
    def _check_quantity(self):
        for record in self:
            if record.init_quantity and record.init_quantity <= 0.0:
                raise ValidationError(_("La cantidad inicial debe ser un valor positivo."))

    def action_register_medication_inventory(self):
        self.ensure_one()
        
        relationship_records = self.env['relationship.resident.family'].search([
            ('resident_id', '=', self.resident_id.id)
        ])
        family_ids = relationship_records.mapped('family_id').ids

        if self.family_id.id not in family_ids:
            raise ValidationError("El familiar seleccionado no tiene ningún parentesco con el residente")

        resident_id = self.resident_id.id
        medicament_id = self.medicament_id.id
        pharmaceutical_form = self.pharmaceutical_form
        uom_id = self.uom_id.id
        cat_uom_id = self.uom_id.category_id.id
        
        # Acceder al modelo MedicationInventory
        MedicationInventory = self.env['medication.inventory'].sudo()
        medication_inventory =MedicationInventory.create({
            'medicament_id': medicament_id,
            'pharmaceutical_form': pharmaceutical_form,
            'resident_id': resident_id,
            'available_quantity': 0,
            'alert_quantity': self.alert_quantity,
            'warning_quantity': self.warning_quantity,
            'uom_id': uom_id,
            'cat_uom_id': cat_uom_id,
            'reason_inventory':self.reason_inventory,
        })

        new_available_quantity = medication_inventory.available_quantity 
        quantity = self.init_quantity
        
        new_available_quantity = new_available_quantity + quantity
        medication_inventory.write(
            {
                'available_quantity': new_available_quantity
            }
        )
        OperationInventory = self.env['operation.inventory'].sudo()
        
        OperationInventory.create(
            {
                'quantity':self.init_quantity,
                'uom_id':uom_id,
                'reason':"Suministro incial del inventario",
                'operation_type':'in',
                'medication_inventory_id': medication_inventory.id,
                'family_id': self.family_id.id ,
            }
        )
