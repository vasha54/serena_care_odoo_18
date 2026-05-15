import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class Resident(models.Model):
    _inherit = 'resident'

    def action_open_create_note_wizard(self):
        """ This method opens the wizard to create a new calendar note """
        return {
            'type': 'ir.actions.act_window',
            'name': 'Registrar nota en el calendario',
            'res_model': 'create.calendar.note.wizard',
            'view_mode': 'form',
            'target': 'new',  # Opens as a pop-up
            'context': {
                'default_user_id': self.env.user.id,
                'default_resident_id': self.id,
            },
        }  
