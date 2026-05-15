import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)

class VitalSigns(models.Model):
    _name = 'vital.signs'
    _description = 'Signos Vitales'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Agregar para tracking
    _order = 'date desc'
    
    resident_id = fields.Many2one(
        'resident', 
        string='Residente',
        required=True,
        ondelete='restrict',
    )
    residence_id =  fields.Many2one(
        string="Residencia",
        related='resident_id.residence_id', 
        readonly=True
    )
    user_id = fields.Many2one(
        'res.users', 
        string='Registrado por', 
        default=lambda self: self.env.user,
        required=True,
        ondelete='restrict',
    )
    date = fields.Datetime(
        string='Fecha/Hora', 
        default=fields.Datetime.now,
        required=True
    )
    temperature = fields.Float(string='Temperatura (°C)', digits=(3,1), tracking=True)
    heart_rate = fields.Integer(string='Frecuencia Cardíaca (lpm)', tracking=True)
    systolic = fields.Integer(string='Tensión Arterial Sistólica (mmHg)', tracking=True)
    diastolic = fields.Integer(string='Tensión Arterial Diastólica (mmHg)', tracking=True)
    respiratory_rate = fields.Integer(string='Frecuencia Respiratoria (rpm)', tracking=True)
    weight = fields.Float(string='Peso (kg)', digits=(4,1), tracking=True)
    oxygen_saturation = fields.Integer(string='Oxigenación (%)',  tracking=True)
    glucose = fields.Float(string='Glucosa (mg/dL)', digits=(4,1), tracking=True)
    grip_strength = fields.Float(string='Fuerza de Presión (kg)', digits=(3,1), tracking=True)
    blood_pressure = fields.Char(
        string='Tensión Arterial',
        compute='_compute_blood_pressure',
        store=True
    )
    history_change = fields.Html(compute='_compute_history_change', sanitize=False,
    strip_style=False, store=False)

    @api.depends('resident_id')
    def _compute_display_name(self):
        for r in self:
            r.display_name = f"Registro de los signos vitales de {r.resident_id.name}"
    
    @api.depends('message_ids')
    def _compute_history_change(self):
        for record in self:
            # Construir un contenedor HTML principal
            logs = '<div class="tracking_history">'
            has_content = False
            
            # Recorrer mensajes en orden cronológico inverso (más reciente primero)
            for message in record.message_ids.sorted(key=lambda m: m.id, reverse=True):
                if message.body:
                    logs += message.body
                    has_content = True
            
            logs += '</div>'
            
            # Mostrar mensaje si no hay contenido
            record.history_change = logs if has_content else '<div class="no_changes"><b>No existen modificaciones</b></div>'
                

    @api.depends('systolic', 'diastolic')
    def _compute_blood_pressure(self):
        for record in self:
            if record.systolic and record.diastolic:
                record.blood_pressure = f"{record.systolic}/{record.diastolic}"
            else:
                record.blood_pressure = ""

    def write(self, vals):
        # Crear registro de auditoría antes de la modificación
        for record in self:
            original_values = {
                field: record[field] for field in self._get_tracked_fields()
            }
        
        result = super(VitalSigns, self).write(vals)
        
        # Crear registro de auditoría después de la modificación
        for record in self:
            updated_values = record.read(self._get_tracked_fields())[0]
            changes = []
            
            for field in self._get_tracked_fields():
                original = original_values.get(field)
                new = updated_values.get(field)
                
                if original != new:
                    field_name = self._fields[field].string
                    changes.append(f"{field_name}: {original} → {new}")
            
            if changes:
                now_utc = fields.Datetime.now()
                now_tz = fields.Datetime.context_timestamp(self, now_utc)
                formatted_date = now_tz.strftime("%Y-%m-%d %H:%M")

                self.env['audit.log'].sudo().create({
                    'name': _('Cambio en signos vitales de %s') % record.resident_id.name,
                    'user_id': self.env.user.id,
                    'model_id': self.env['ir.model']._get_id('vital.signs'),
                    'record_id': record.id,
                    'action_type': 'change_vital_signs',
                    'details': "\n".join(changes)
                })
        #         body = _("""
        #     <div class="tracking_changes">
        #         <b>Cambios realizados el %s por %s:</b>
        #         <ul>%s</ul>
        #     </div>
        # """) % (
        #     formatted_date,
        #     self.env.user.name,
        #     ''.join([f'<li>{change}</li>' for change in changes])
        # )
                
        #         # Publicar en el chatter
        #         record.message_post(body=body)
        
        return result
    
    def _get_tracked_fields(self):
        """Obtener lista de campos con tracking activado"""
        return [name for name, field in self._fields.items() 
                if getattr(field, 'tracking', False)]
        
    def unlink(self):
        # Antes de eliminar, crear logs para cada registro
        for record in self:
            self.env['audit.log'].sudo().crud_audit_log(record, 'vital.signs', 'unlink')
        return super().unlink()
    
    @api.model
    def create(self, values):
        records = super().create(values)
        # Crear log de auditoría para cada registro creado
        for record in records:
            self.env['audit.log'].sudo().crud_audit_log(record, 'vital.signs', 'create')
        return records