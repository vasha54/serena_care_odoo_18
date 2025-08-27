# -*- coding: utf-8 -*-
import base64
import os
from email import message
import logging
import datetime
from os import unlink
import re
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class ResidenceHouse(models.Model):
    _name = "residence_house"
    _description = "Casas de Residencia"
    _order = "name"
    _inherit = ["soft.delete.mixin"]
    _inherits = {"res.partner": "partner_id"}

    partner_id = fields.Many2one(
        "res.partner",
        string="Contacto",
        required=True,
        ondelete="cascade",
    )

    description = fields.Html(string="Descripción")
    schedule = fields.Char(string="Horario de Atención", size=255)
    services_ids = fields.Many2many("residence_service", string="Servicios")
    image_with_default = fields.Binary(
        string="Imagen con valor por defecto",
        compute="_compute_image_with_default",
        store=False,
    )

    @api.depends("image_1920")
    def _compute_image_with_default(self):
        default_image_path = os.path.join(
            os.path.dirname(__file__), "..", "static", "src", "img", "default_house.png"
        )
        # Leer la imagen por defecto si existe
        default_image = None
        if os.path.exists(default_image_path):
            with open(default_image_path, "rb") as f:
                default_image = base64.b64encode(f.read())

        for record in self:
            if record.image_1920:
                record.image_with_default = record.image_1920
            else:
                record.image_with_default = default_image

    @api.constrains("email")
    def _check_valid_email(self):
        for record in self:
            if record.email:
                # Regex para validar email con dominio correcto
                pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
                if not re.match(pattern, record.email):
                    raise ValidationError(
                        "Formato de correo inválido. Debe tener un formato válido como: ejemplo@dominio.com"
                    )

    @api.constrains("name")
    def _check_name_format(self):
        for record in self:
            if record.name:
                # Verificar que sólo contenga letras y espacios
                if not re.match(r"^[A-Za-záéíóúÁÉÍÓÚñÑüÜ\s]+$", record.name):
                    raise ValidationError(
                        "El nombre sólo debe contener letras y espacios."
                    )
                # Verificar que comience con mayúscula
                if not record.name[0].isupper():
                    raise ValidationError(
                        "El nombre debe comenzar con una letra mayúscula."
                    )

    @api.constrains("phone")
    def _check_phone_format(self):
        """Valida que el teléfono tenga formato mexicano válido (10 dígitos, con o sin +52)"""
        for record in self:
            if record.phone:
                # Eliminar TODOS los caracteres no numéricos (incluye +, espacios, guiones, etc.)
                clean_phone = re.sub(r"\D", "", record.phone)

                # Verificar si es número con código de país (12 dígitos incluyendo +52)
                if len(clean_phone) == 12 and clean_phone.startswith("52"):
                    clean_phone = clean_phone[2:]  # Remover código de país (52)

                # Validar longitud (10 dígitos después de limpiar)
                if len(clean_phone) != 10 or not clean_phone.isdigit():
                    raise ValidationError(
                        "Formato de teléfono inválido. Debe ser de 10 dígitos o incluir código de país (+52). "
                        "Ejemplos: 5512345678, 55 1234 5678, +525512345678"
                    )

    def unlink(self):
        residents = 0
        employees = 0

        if "resident_count" in self.env["residence_house"].fields_get():
            residents = self.resident_count
        else:
            _logger.warning("No find field 'resident_count' in model 'residence_house'")

        if "employee_count" in self.env["residence_house"].fields_get():
            employees = self.employee_count
        else:
            _logger.warning("No find field 'resident_count' in model 'residence_house'")

        if residents > 0 or employees > 0:
            message = f"No se puede eliminar la residencia {self.name}. "
            message += f"Reubique primero los residentes ({residents}) y empleados ({employees}) de la residencia."
            raise ValidationError(message)

        return self.action_soft_delete()

    def write(self, vals):
        # Verificar si se está intentando desactivar el registro
        if "active" in vals and not vals["active"]:
            # Para cada registro que se está modificando
            for record in self:
                # Verificar si el campo resident_ids existe y tiene registros
                resident_count = 0
                if hasattr(record, "resident_ids"):
                    resident_count = len(record.resident_ids)

                # Verificar si el campo employee_ids existe y tiene registros
                employee_count = 0
                if hasattr(record, "employee_ids"):
                    employee_count = len(record.employee_ids)

                # Si hay residentes o empleados, prevenir la desactivación
                if resident_count > 0 or employee_count > 0:
                    raise UserError(
                        _(
                            'No se puede desactivar la residencia "%s" porque tiene %d residente(s) y %d empleado(s) asignado(s). '
                            "Por favor, reasigne estos recursos antes de desactivar."
                        )
                        % (record.name, resident_count, employee_count)
                    )

        # Si todas las validaciones pasan, ejecutar la lógica original de write
        return super().write(vals)
