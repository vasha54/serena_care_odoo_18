import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied

_logger = logging.getLogger(__name__)

class Employee(models.Model):
    _inherit = 'hr.employee'

    show_delete_button_cv = fields.Boolean(compute='_compute_show_button', store=False)
    cv_preview_url = fields.Char(
        string="URL de previsualización",
        compute='_compute_cv_preview_url',
        store=False
    )

    def _compute_show_button(self):
        for record in self:
            record.show_delete_button_cv = self.env.context.get('default_readonly', False)

    @api.depends('cv_attachment_id')
    def _compute_cv_preview_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for employee in self:
            if employee.cv_attachment_id:
                employee.cv_preview_url = f"{base_url}/web/content/{employee.cv_attachment_id.id}?download=true"
            else:
                employee.cv_preview_url = False
 
        
    def action_view_details(self):
        """Abrir vista de formulario en modo solo lectura"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'view_id': self.env.ref('sc_employee.view_residence_employee_form').id,
            'target': 'current',
            'flags': {'mode': 'readonly'},
            'context': {
                'default_readonly': True,
            }
        }

    def action_edit(self):
        """Abrir vista de formulario en modo edición"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'view_id': self.env.ref('sc_employee.view_residence_employee_form').id,
            'target': 'current',
        }

    def action_upload_avatar(self):
        """Abrir vista de formulario en modo edición"""
        self.ensure_one()
        return {
            'name': f"Cambiar la imagen del empleado: {self.name}",
            'type': 'ir.actions.act_window',
            'res_model': 'change.photo.employee.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_current_employee_id': self.id,
            }
        }

    def action_upload_certificate(self):
        self.ensure_one()
        return {
            'name': f"Subir nuevo certificado del empleado: {self.name}",
            'type': 'ir.actions.act_window',
            'res_model': 'hr.employee.certificate',
            'res_id': False,
            'view_mode': 'form',
            'view_id': self.env.ref('sc_employee.view_hr_employee_certificate_form').id,
            'target': 'new',
            'context': {
                'default_current_employee_id': self.id,
            }
        }

    def action_preview_cv(self):
        """Abrir el CV en una nueva pestaña"""
        self.ensure_one()
        if self.cv_attachment_id:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            url = f"{base_url}/web/content/{self.cv_attachment_id.id}"
            return {
                'type': 'ir.actions.act_url',
                'url': url,
                'target': 'new'
            }
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Error',
                'message': 'No hay CV para previsualizar',
                'type': 'warning',
                'sticky': False,
            }
        }

    def action_download_cv(self):
        """Descargar el CV"""
        self.ensure_one()
        if self.cv_attachment_id:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            url = f"{base_url}/web/content/{self.cv_attachment_id.id}?download=true"
            return {
                'type': 'ir.actions.act_url',
                'url': url,
                'target': 'self'
            }
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Error',
                'message': 'No hay CV para descargar',
                'type': 'warning',
                'sticky': False,
            }
        }

    def unlink_cv_attachment(self):
        """Eliminar el CV"""
        for employee in self:
            if employee.cv_attachment_id:
                employee.cv_attachment_id.unlink()
            employee.write({
                'cv_file': False,
                'cv_filename': False,
                'cv_attachment_id': False
            })
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
            'params': {
                'title': 'Éxito',
                'message': 'CV eliminado correctamente',
                'type': 'success',
                'sticky': False,
            }
        }


     

    
    