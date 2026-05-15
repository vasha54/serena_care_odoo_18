from odoo import models, fields, api

class CalendarNote(models.Model):
    _name = 'calendar.note'
    _description = 'Notas calendariadas'

    resident_id = fields.Many2one(
        'resident', 
        string='Residente',
        required=True,
        ondelete='restrict',
    )
    name = fields.Char(string='Nombre', required=True)
    start_date = fields.Datetime(string='Fecha', required=True)
    # stop_date = fields.Datetime(string='End Date', required=True)
    description = fields.Text(string='Descripción')
    user_id = fields.Many2one(
        'res.users', 
        string='Registrado por', 
        default=lambda self: self.env.user,
        required=True,
        ondelete='restrict',
    )
    event_type = fields.Selection(
        string='Tipo de Anotación',
        selection=[
            ('note', 'Nota'), 
            ('appointment_doctor', 'Cita médica')
        ],
        default='note',
        required=True
    )
    doctor_id = fields.Many2one(
        'supplier.base',
        string='Doctor',
        domain=[("active", "=", True),("provider_type", "in", ["specialist", "doctor"])],
        ondelete="restrict",
    )
    specialty_doctor =  fields.Many2one(
        string="Especialidad",
        related='doctor_id.nomenclature_specialty_id', 
        readonly=True
    )
    description_compute = fields.Text(
        string='Descripción',
        compute='_compute_description_compute',
        store=True,
    )
    date_vaca =  fields.Char(string="Fecha de VACA")
    
    @api.depends('description','event_type','doctor_id')
    def _compute_description_compute(self):
        for record in self:
            record.description_compute = record.description
            if record.event_type == 'appointment_doctor' and record.doctor_id:
                record.description_compute = f"Cita médica con {record.doctor_id.name}, "
                f"{record.specialty_doctor.name}. {record.description}"
    
    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        # Obtener el resident_id del contexto
        resident_id = self.env.context.get('default_resident_id')
        if resident_id:
            res['resident_id'] = resident_id
        return res
            
    @api.model
    def create(self, values):
        records = super().create(values)
        # Crear log de auditoría para cada registro creado
        for record in records:
            self.env['audit.log'].sudo().crud_audit_log(record, 'calendar.note', 'create')
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
            self.env['audit.log'].sudo().crud_audit_log(record, 'calendar.note', 'write', extra_details=details)
        return result

    def unlink(self):
        # Antes de eliminar, crear logs para cada registro
        for record in self:
            self.env['audit.log'].sudo().crud_audit_log(record, 'calendar.note', 'unlink')
        return super().unlink()
