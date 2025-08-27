import logging
import re
from dateutil.relativedelta import relativedelta
from datetime import date

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)


class Resident(models.Model):
    _name = 'resident'
    _description = 'Resident Model'
    _inherit  = ['soft.delete.mixin']
    _inherits = {'res.partner': 'partner_id'}

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Contacto',
        required=True,
        ondelete='cascade'
    )
    dni = fields.Char(
        string="DNI",
        required=True,
        size=13,
    )
    sex_id = fields.Many2one(
        comodel_name='res.sex',
        string='Sexo',
        required=True,
        help='Sexo a la que pertenece el residente',
    )
    weight = fields.Float(
        string='Peso (Kg)',
        required=True,
        help='Peso del residente',
    )    
    residence_id = fields.Many2one(
        comodel_name='residence_house',
        string='Residencia',
        required=True,
        help='Residencia a la que pertenece el residente',
        domain="[('active', '=', True),('is_deleted','=',False)]"
    )
    birth_date = fields.Date(
        string='Fecha de Nacimiento',
        required=True,
        help='Fecha de nacimiento del residente'
    )
    country_id = fields.Many2one(
        comodel_name='res.country',
        string='País',
        default=lambda self: self.env.ref('base.mx',False),
        help='País de origen del residente'
    )
    age = fields.Integer(
        string='Edad',
        compute='_compute_age',
        store=True,
        help='Edad calculada a partir de la fecha de nacimiento'
    )
    family_ids = fields.One2many(
        'relationship.resident.family', 
        'resident_id',
        string='Familiares',
        help="Familiares asociados a este residente"
    )
    diagnosis = fields.Text(
        string='Diagnóstico',
    )
    risk_falling = fields.Text(
        string='Riesgo de caída',
    )
    risk_upp = fields.Text(
        string='Riesgo de UPP',
    )
    observations = fields.Text(
        string='Observaciones',
    )
    allergy_ids = fields.Many2many(
        comodel_name='nomenclature.allergy',
        relation='model_resident_allergy_ref',
        string="Alergías",
        help='Alergías que pedece el residente'
    )

    _sql_constraints = [
        ('name_resident_unique', 'UNIQUE(name)', 'El nombre del residente debe ser único!'),
    ]

    @api.constrains('dni')
    def _check_dni_format(self):
        """Valida que el DNI tenga máximo 13 caracteres y sea alfanumérico"""
        for record in self:
            if record.dni:
                # Verificar longitud máxima
                if len(record.dni) > 13:
                    raise ValidationError(_('El DNI no puede tener más de 13 caracteres.'))
                
                # Verificar que sea alfanumérico (permite letras y números)
                if not re.match(r'^[a-zA-Z0-9]+$', record.dni):
                    raise ValidationError(_('El DNI solo puede contener letras y números.'))

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

    @api.depends('birth_date')
    def _compute_age(self):
        for record in self:
            if record.birth_date:
                today = date.today()
                birth_date = fields.Date.from_string(record.birth_date)
                record.age = relativedelta(today, birth_date).years
            else:
                record.age = 0

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

    def unlink(self):
        if not self.active:
           raise UserError(f"No se puede eliminar el residente {self.name} por estar inactivo")

        model_id = self.env['ir.model']._get('resident').id
        AuditLog = self.env['audit.log'].sudo()
        AuditLog.create({
            'name': f"Se eliminó el residente {self.name}",
            'user_id': self.env.user.id,
            'model_id': model_id,
            'record_id': self.id,
            'action_type': 'unlink',
            'details': f"El residente se encontraba en la residencia {self.residence_id.name} en" 
                    " el momento que fue eliminado del sistema"
        })
        return self.action_soft_delete()

    @api.model
    def create(self, vals):
        if vals.get('name'):
            self._check_unique_name(vals['name'])
        vals['is_company'] = False
        return super().create(vals)

    def write(self, vals):

        if not vals.get('active'):
            for record in self:
               if not record.active:
                    raise UserError(f"No se puede modificar el residente {record.name} por estar inactivo")

        if vals.get('name'):
            for record in self:
                self._check_unique_name(vals['name'], record.id)
        return super().write(vals)


    def _check_unique_name(self, name, exclude_id=None):
        domain = [('name', '=', name)]
        if exclude_id:
            domain.append(('id', '!=', exclude_id))
        if self.search_count(domain) > 0:
            raise ValidationError("El nombre del residente debe ser único!")

    def _cron_update_age(self):
        _logger.info("Iniciando actualización diaria de edades de residentes")
        residents = self.search([])
        residents._compute_age()
        _logger.info(f"Edades actualizadas para {len(residents)} residentes")



class NomenclatureAllergy(models.Model):
    _name = 'nomenclature.allergy'

    active = fields.Boolean(string='Activa', default=True)
    name =  fields.Char(string="Nombre", required=True)
    slug = fields.Char(
        string="Slug", compute="_compute_slug", readonly=True, store=True
    )
    resident_ids = fields.Many2many(
        comodel_name='resident',
        relation='model_resident_allergy_ref',
        string="Residentes",
        help='Residentes que padecen esta alergía'
    )

    @api.depends("name")
    def _compute_slug(self):
        for record in self:
            record.slug = self._generate_slug(record.name)

    def _generate_slug(self, name):
        cleaned = re.sub(r"[^\w\-]+", "", str(name))
        slug = cleaned.replace(" ", "-")
        return slug.lower()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['name'] = vals.get('name', '')
            existing_record_slug = self.search(
                [
                    ("slug", "=", self._generate_slug(vals.get("name"))),
                ],
                limit=1,
            )

            if existing_record_slug:
                raise ValidationError(
                    f"Una alergía con nombre '{vals['name']}' ya existe."
                )


        return super().create(vals_list)

    def write(self, vals):
        if "name" in vals:
            vals['name'] = vals['name']
            existing_record_slug = self.search(
                [
                    ("slug", "=", self._generate_slug(vals.get("name"))),
                    ("id", "!=", self.id),
                ],
                limit=1,
            )

            if existing_record_slug:
                raise ValidationError(
                    f"Una alergía con nombre '{vals['name']}' ya existe."
                )

        return super().write(vals)

    def unlink(self):
        for record in self:
            if record.resident_ids:
                residents =record.resident_ids.mapped('name')
                raise UserError(
                    _("No se puede eliminar la alergía %s porque está siendo utilizado en:\n- %s") % 
                    (record.name, "\n- ".join(residents))
                )
        return super().unlink()

    def toggle_active(self):
        for record in self:
            if record.active and record.resident_ids:
                raise UserError(
                    "No se puede desactivar una alergía que está en uso."
                )
        return super().toggle_active()