import re
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError

import logging
_logger = logging.getLogger(__name__)

class LaboratoryFile(models.Model):
    _name = 'laboratory.file'
    _description = 'Fichero de estudio de laboratorio del residente'
    _order = 'date desc'

    resident_id = fields.Many2one(
        'resident', 
        string='Residente',
        required=True,
        ondelete='restrict',
        default=lambda self: self.env.context.get('default_current_resident_id')
    )
    residence_id =  fields.Many2one(
        string="Residencia",
        related='resident_id.residence_id', 
        readonly=True
    )
    date = fields.Datetime(
        string='Fecha/Hora', 
        default=fields.Datetime.now,
        required=True
    )
    description = fields.Text(string='Descripción')
    user_id = fields.Many2one(
        'res.users', 
        string='Registrado por', 
        default=lambda self: self.env.user,
        required=True,
        ondelete='restrict',
    )
    laboratory_file = fields.Binary(
        string='Archivo del Laboratorio',
        required=True,
        attachment=True
    )
    laboratory_filename = fields.Char(string='Nombre del Archivo')
    
    laboratory_attachment_id = fields.Many2one(
        'ir.attachment',
        string="Fichero",
        domain="[('res_model', '=', 'laboratory.file'), ('res_id', '=', id)]"
    )
    
    is_image_file = fields.Boolean(
        string="Es archivo de imagen",
        compute="_compute_file_type",
        store=False  # Se calcula al vuelo, no se guarda en BD
    )
    is_pdf_file = fields.Boolean(
        string="Es archivo PDF",
        compute="_compute_file_type",
        store=False
    )

    @api.depends('laboratory_filename')
    def _compute_file_type(self):
        for record in self:
            record.is_image_file = False
            record.is_pdf_file = False
            if record.laboratory_filename:
                filename_lower = record.laboratory_filename.lower()
                # Comprobar si es una imagen
                record.is_image_file = filename_lower.endswith(('.png', '.jpg', '.jpeg'))
                # Comprobar si es un PDF
                record.is_pdf_file = filename_lower.endswith('.pdf')
    
    @api.constrains('laboratory_filename')
    def _check_file_extension(self):
        for record in self:
            if record.laboratory_filename:
                extension = record.laboratory_filename.split('.')[-1].lower()
                allowed_extensions = ['pdf', 'png', 'jpg', 'jpeg']
                if extension not in allowed_extensions:
                    raise ValidationError(
                        "Solo se permiten archivos con extensiones: %s" % 
                        ', '.join(['.' + ext for ext in allowed_extensions])
                    )
    
    @api.model
    def create(self, vals):
        record = super(LaboratoryFile, self).create(vals)
         # Crear logs de auditoría para cada registro creado
        for r in record:
            self.env['audit.log'].sudo().crud_audit_log(r, 'laboratory.file', 'create')
        # Manejo de attachments (código original)
        # Si se subió un archivo pero no hay attachment_id, crearlo
        if record.laboratory_file and not record.laboratory_attachment_id:
            attachment = self.env['ir.attachment'].create({
                'name': record.laboratory_filename or record.name,
                'datas': record.laboratory_file,
                'res_model': 'laboratory.file',
                'res_id': record.id,
                'type': 'binary',
            })
            attachment.write({'access_token': attachment._generate_access_token()})
            record.laboratory_attachment_id = attachment.id
        return record
    
    def write(self, vals):
        # Guardar estado anterior para detectar cambios (solo campos almacenados)
        old_values = {}
        for record in self:
            old_values[record.id] = {
                field: record[field] for field in vals if field in record._fields and not record._fields[field].compute
            }
        result = super(LaboratoryFile, self).write(vals)
        # Registrar auditoría con detalles de cambios
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
            self.env['audit.log'].sudo().crud_audit_log(record, 'laboratory.file', 'write', extra_details=details)
        # Si se actualizó el archivo, actualizar el attachment
        if 'laboratory_file' in vals:
            for record in self:
                if record.laboratory_attachment_id:
                    record.laboratory_attachment_id.write({
                        'datas': record.laboratory_file,
                        'name': record.laboratory_filename or record.name,
                        'access_token': record.laboratory_attachment_id._generate_access_token()
                    })
                    
                else:
                    attachment = self.env['ir.attachment'].create({
                        'name': record.laboratory_filename or record.name,
                        'datas': record.laboratory_file,
                        'res_model': 'laboratory.file',
                        'res_id': record.id,
                        'type': 'binary',
                    })
                    attachment.write({'access_token': attachment._generate_access_token()})
                    record.laboratory_attachment_id = attachment.id
        return result
    
    def unlink(self):
        # Registrar auditoría antes de eliminar
        for record in self:
            self.env['audit.log'].sudo().crud_audit_log(record, 'laboratory.file', 'unlink')
        return super(LaboratoryFile, self).unlink()
    
    @api.depends('resident_id')
    def _compute_display_name(self):
        for r in self:
            r.display_name = f"Estudio de laboratorio: {r.resident_id.name}"
