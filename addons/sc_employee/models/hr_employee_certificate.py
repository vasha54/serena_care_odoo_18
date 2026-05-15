from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
import logging
import base64 
import os
import urllib.parse


_logger = logging.getLogger(__name__)

class HrEmployeeCertificate(models.Model):
    _name = 'hr.employee.certificate'
    _description = 'Certificado del Empleado'
    
    name = fields.Char(string='Nombre del Certificado', required=True)
    employee_id = fields.Many2one(
        'hr.employee',
        string='Empleado',
        required=True,
        default=lambda self: self.env.context.get('default_current_employee_id')
    )
    certificate_file = fields.Binary(
        string='Archivo del Certificado',
        required=True,
        attachment=True
    )
    certificate_filename = fields.Char(string='Nombre del Archivo')
    issue_date = fields.Date(string='Fecha de Emisión')
    expiration_date = fields.Date(string='Fecha de Expiración')
    institution = fields.Char(string='Institución')
    description = fields.Text(string='Descripción')
    is_valid = fields.Boolean(
        string='Válido',
        compute='_compute_is_valid',
        store=True
    )
    certificate_attachment_id = fields.Many2one(
        'ir.attachment',
        string="Certificado",
        domain="[('res_model', '=', 'hr.employee.certificate'), ('res_id', '=', id)]"
    )
    
    
    
    
    @api.depends('expiration_date')
    def _compute_is_valid(self):
        for certificate in self:
            if certificate.expiration_date:
                certificate.is_valid = certificate.expiration_date >= fields.Date.today()
            else:
                certificate.is_valid = True

    @api.constrains('certificate_filename')
    def _check_file_extension(self):
        for record in self:
            if record.certificate_filename:
                extension = record.certificate_filename.split('.')[-1].lower()
                allowed_extensions = ['pdf', 'png', 'jpg', 'jpeg']
                if extension not in allowed_extensions:
                    raise ValidationError(
                        "Solo se permiten archivos con extensiones: %s" % 
                        ', '.join(['.' + ext for ext in allowed_extensions])
                    )
    
    @api.model
    def create(self, vals):
        records = super(HrEmployeeCertificate, self).create(vals)
        # Si se subió un archivo pero no hay attachment_id, crearlo
        if records.certificate_file and not records.certificate_attachment_id:
            attachment = self.env['ir.attachment'].create({
                'name': records.certificate_filename or records.name,
                'datas': records.certificate_file,
                'res_model': 'hr.employee.certificate',
                'res_id': records.id,
                'type': 'binary',
            })
            records.certificate_attachment_id = attachment.id
        # Crear log de auditoría para cada registro creado
        for record in records:
            self.env['audit.log'].sudo().crud_audit_log(record, 'hr.employee.certificate', 'create')
        return records
    
    def write(self, vals):
        old_values = {}
        for record in self:
            old_values[record.id] = {
                field: record[field] for field in vals if field in record._fields and not record._fields[field].compute
            }
        results = super(HrEmployeeCertificate, self).write(vals)
        # Si se actualizó el archivo, actualizar el attachment
        if 'certificate_file' in vals:
            for record in self:
                if record.certificate_attachment_id:
                    record.certificate_attachment_id.write({
                        'datas': record.certificate_file,
                        'name': record.certificate_filename or record.name
                    })
                else:
                    attachment = self.env['ir.attachment'].create({
                        'name': record.certificate_filename or record.name,
                        'datas': record.certificate_file,
                        'res_model': 'hr.employee.certificate',
                        'res_id': record.id,
                        'type': 'binary',
                    })
                    record.certificate_attachment_id = attachment.id
        # Después de la escritura, crear logs con los campos modificados
        for record in self:
            changed_fields = []
            for field, new_val in vals.items():
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
            self.env['audit.log'].sudo().crud_audit_log(record, 'hr.employee.certificate', 'write', extra_details=details)
        return results
    
    def unlink(self):
        # Antes de eliminar, crear logs para cada registro
        for record in self:
            self.env['audit.log'].sudo().crud_audit_log(record, 'hr.employee.certificate', 'unlink')
        return super().unlink()
