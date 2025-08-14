from odoo import models, api, fields
import logging

_logger = logging.getLogger(__name__)

class BaseModel(models.AbstractModel):
    _inherit = 'base'
    
    def toggle_active(self):
        super().toggle_active()
        return {
            'type':'ir.actions.client',
             'tag':'reload',
        }

    def write(self, vals):
        # Verificar si 'active' está siendo modificado y el modelo tiene este campo
        if 'active' in vals and 'active' in self._fields:
            # Guardar valores antiguos de 'active' {id: valor}
            old_active_map = {rec.id: rec.active for rec in self}
            
            # Ejecutar el write original
            result = super().write(vals)
            
            # Buscar el modelo correspondiente en ir.model
            model = self.env['ir.model'].search([('model', '=', self._name)], limit=1)
            new_active = vals['active']
            
            logs = []
            for rec in self:
                old_active = old_active_map.get(rec.id)
                # Comparar valores antiguo y nuevo
                if old_active != new_active:
                    logs.append({
                        'name': f"Cambio estado activo: {model.name} ({self._name}) ID {rec.id} " + (f"Nombre {rec.name}" if rec.name else ""),
                        'user_id': self.env.user.id,
                        'model_id': model.id,
                        'record_id': rec.id,
                        'action_type': 'activate_deactivate',
                        'details': f"Campo 'active' modificado: {old_active} → {new_active}"
                    })
            
            # Crear registros de auditoría en lote
            if logs:
                self.env['audit.log'].sudo().create(logs)
                
            return result
        return super().write(vals)

