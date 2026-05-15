import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)

#TODO Falta garantizar en el formulario de esta vista que solo salgan
# los familiares especificos del familiar
class OperationInventoryCreateWizard(models.TransientModel):
    _name = 'operation.inventory.create.wizard'
    _description = 'Crear el inventario de un medicamento para un residente desde la vista del residente que no responde a ninguna indicación médica de tipo medicamento'

    operation_type = fields.Selection(
        [("in", "Entrada"), ("out", "Salida"), ("adjust", "Ajuste")],
        string="Tipo de Operación",
        required=True,
        default=lambda self: self._get_default_operation()
    )
    resident_id = fields.Many2one(
        'resident', 
        string='Residente',
        required=True,
        default=lambda self: self._get_default_resident()
    )
    quantity = fields.Float(string="Cantidad", required=True)
    medication_inventory_id = fields.Many2one(
        string='Inventario', 
        comodel_name='medication.inventory', 
        ondelete='restrict'
    )
    medicament_id = fields.Many2one(
        related='medication_inventory_id.medicament_id',
        readonly=True,
        string="Medicamento", 
        required=True
    )
    pharmaceutical_form = fields.Char(
        related='medication_inventory_id.pharmaceutical_form',
        readonly=True,
        string='Forma Farmacéutica', 
        required=True, 
    )
    uom_id = fields.Many2one(
        related='medication_inventory_id.uom_id',
        readonly=True,
        string='Forma Farmacéutica', 
        required=True
    )
    reason = fields.Text(
        string="Motivo de la operación", 
        required=True
    )
    family_id = fields.Many2one(
        'resident.family', 
        string='Familiar',
        domain="[('id', 'in', available_family_ids)]"
    )
    date = fields.Datetime(
        string='Fecha/Hora', 
        default=fields.Datetime.now,
        required=True
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

    def _get_default_operation(self):
        # Obtener operación del contexto
        return self.env.context.get('default_operation')

    @api.constrains('quantity')
    def _check_quantity(self):
        for record in self:
            if record.quantity and record.quantity <= 0.0:
                raise ValidationError(_("La cantidad ha agregar/disminuir debe ser un valor positivo."))

    def action_register_operation_inventory(self):
        self.ensure_one()
        
        relationship_records = self.env['relationship.resident.family'].search([
            ('resident_id', '=', self.resident_id.id)
        ])
        family_ids = relationship_records.mapped('family_id').ids

        if self.operation_type == 'in' and self.family_id.id not in family_ids:
            raise ValidationError("El familiar seleccionado no tiene ningún parentesco con el residente")

        if self.operation_type == 'out' and self.quantity > self.medication_inventory_id.available_quantity:
            raise ValidationError("La cantidad que se desea extraer no está disponible en el inventario actual del medicamento")

        new_available_quantity = self.medication_inventory_id.available_quantity 
        quantity = self.quantity
        if self.operation_type == 'out':
            quantity = quantity * (-1)
        
        new_available_quantity = new_available_quantity + quantity
        self.medication_inventory_id.write(
            {
                'available_quantity': new_available_quantity
            }
        )
        OperationInventory = self.env['operation.inventory'].sudo()
        
        OperationInventory.create(
            {
                'quantity':self.quantity,
                'uom_id':self.uom_id.id,
                'reason':self.reason,
                'operation_type':self.operation_type,
                'medication_inventory_id': self.medication_inventory_id.id,
                'family_id': self.family_id.id if self.operation_type == 'in' else False,
                'date': self.date,
            }
        )
        