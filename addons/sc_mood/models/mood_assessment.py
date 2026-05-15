import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class MoodAssessment(models.Model):
    _name = "mood.assessment"
    _description = "Evaluación del ánimo del residente"
    _order = 'date desc'

    resident_id = fields.Many2one("resident", string="Residente", required=True)
    residence_id =  fields.Many2one(
        string="Residencia",
        related='resident_id.residence_id', 
        readonly=True
    )
    mood_state_id = fields.Many2one(
        "mood.state",
        string="Estado de ánimo",
        ondelete="restrict",

    )
    user_id = fields.Many2one(
        "res.users",
        string="Registrado por",
        default=lambda self: self.env.user,
        required=True,
        ondelete="restrict",
    )
    mood_state_display = fields.Char(
        string="Estado de ánimo",
        compute="_compute_mood_state_display",
        index=True,
        store=True
    )
    observations_clinic = fields.Text(string="Observaciones clínica")
    image = fields.Binary(string="Icono", related='mood_state_id.image', readonly=True)
    date = fields.Datetime(
        string='Fecha/Hora', 
        default=fields.Datetime.now,
        required=True
    )

    @api.depends("mood_state_id")
    def _compute_mood_state_display(self):
        for asses in self:
            asses.mood_state_display = (
                asses.mood_state_id.name
                if asses.mood_state_id
                else "Fuera de la escala evaluable"
            )

    @api.depends('resident_id','create_date')
    def _compute_display_name(self):
        for r in self:
            r.display_name = f"Evaluación de ánimo de {r.resident_id.name} realizada {r.create_date.strftime('%Y-%m-%d %H:%M')}"
            
    @api.model
    def create(self, values):
        records = super().create(values)
        # Crear log de auditoría para cada registro creado
        for record in records:
            self.env['audit.log'].sudo().crud_audit_log(record, 'mood.assessment', 'create')
        return records

    def write(self, values):
        # Guardar estado anterior para detectar cambios (opcional, mejora la calidad del detalle)
        old_values = {}
        for record in self:
            old_values[record.id] = {
                field: record[field] for field in values if field in record._fields and not record._fields[field].compute
            }
        result = super().write(values)
        # Después de la escritura, crear logs con los campos modificados
        for record in self:
            changed_fields = []
            for field, new_val in values.items():
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
            self.env['audit.log'].sudo().crud_audit_log(record, 'mood.assessment', 'write', extra_details=details)
        return result

    def unlink(self):
        # Antes de eliminar, crear logs para cada registro
        for record in self:
            self.env['audit.log'].sudo().crud_audit_log(record, 'mood.assessment', 'unlink')
        return super().unlink()
