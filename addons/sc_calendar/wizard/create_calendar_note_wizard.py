from odoo import models, fields, api

class CreateCalendarNoteWizard(models.TransientModel):
    _name = 'create.calendar.note.wizard'
    _description = 'Wizard para crear una nota en el calendario'

    name = fields.Char(string='Nombre', required=True)
    start_date = fields.Datetime(string='Fecha', required=True)
    description = fields.Text(string='Descripción')
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

    def action_create_calendar_note(self):
        # Get the active resident record
        resident_id = self.env.context.get('active_id')
        # Create a new calendar.note record
        data = {
            'resident_id': resident_id,
            'name': self.name,
            'start_date': self.start_date,
            'description': self.description,
            'user_id': self.env.user.id,
            'event_type': self.event_type,
        }
        if self.event_type == 'appointment_doctor':
            data['doctor_id'] = self.doctor_id.id
            
        note = self.env['calendar.note'].create(data)
        
        # Close the wizard
        return {'type': 'ir.actions.act_window_close'}