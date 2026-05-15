import logging
import re
import os
import base64
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
        domain=lambda self: [
            ('active', '=', True),
            ('is_deleted', '=', False),
            # ('id', 'in', self.env.user.selected_residences_ids.ids)
        ]
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
    mother_family_history = fields.Text(
        string='Antencedentes Heredofamiliares - Madre',
    )
    father_family_history = fields.Text(
        string='Antencedentes Heredofamiliares - Padre',
    )
    personal_pathological_history = fields.Text(
        string='Antecedentes personales patológicos',
    )
    allergy_ids = fields.Many2many(
        comodel_name='nomenclature.allergy',
        relation='model_resident_allergy_ref',
        string="Alergias",
        help='Alergias que pedece el residente'
    )
    addiction_ids = fields.Many2many(
        comodel_name='nomenclature.addiction',
        relation='model_resident_addiction_ref',
        string="Adicciones",
        help='Adicciones que pedece el residente'
    )
    image_with_default = fields.Binary(
        string="Imagen con valor por defecto",
        compute="_compute_image_with_default",
        store=False,
    )
    is_biomass_exposure = fields.Boolean(
        string="Exposición a Biomasas",
    )
    is_smoking = fields.Boolean(
        string="Tabaquismo",
    )
    is_alcoholism = fields.Boolean(
        string="Alcoholismo",
    )
    fur = fields.Text(
        string="FUR",
    )
    immunizations = fields.Text(
        string="Inmunizaciones",
    )
    p3_p2_ao_co = fields.Text(
        string="P.3 P.2 A.O C.O",
    )


    # Campos para el familiar por defecto inicial
    family_name = fields.Char( 
        string='Nombre del familiar', 
        trasient=True
    )
    family_phone = fields.Char( 
        string='Teléfono del familiar', 
        trasient=True)
    family_mobile = fields.Char( 
        string='Móvil del familiar', 
        trasient=True
    )
    family_email = fields.Char( 
        string='Email del familiar', 
        trasient=True
    ) 
    family_image_1920 = fields.Binary( 
        string='Foto del familiar',
        trasient=True
    )
    family_address = fields.Text(
        string="Dirección del familiar",
        trasient=True
    )
    is_contractor = fields.Boolean(
        string="Contratante",
        default=False
    )
    kinship_id = fields.Many2one( 
        'family.kinship', 
        string='Parentesco', 
        trasient=True
    )
    auth_level_ids = fields.Many2many(
        'auth.level', 
        string='Niveles de autorización',
        help="Actividades que el familiar puede realizar con el paciente", 
        trasient=True
    )
    
    _sql_constraints = [
        ('name_resident_unique', 'UNIQUE(name)', 'El nombre del residente debe ser único!'),
    ]

    @api.depends("image_1920")
    def _compute_image_with_default(self):
        default_image_path = os.path.join(
            os.path.dirname(__file__), "..", "static", "src", "img", "photo_profile_default.png"
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

    @api.depends("family_email")
    def _check_valid_family_email(self):
        for record in self:
            if record.family_email:
                # Regex para validar email con dominio correcto
                pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
                if not re.match(pattern, record.family_email):
                    raise ValidationError(
                        "Formato de correo inválido. Debe tener un formato válido como: ejemplo@dominio.com"
                    )

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
        record = super().create(vals)
        if 'family_name' in vals:
            family_name = vals.pop('family_name')
            family_phone = vals.pop('family_phone',False)
            family_image_1920 = vals.pop('family_image_1920',False)
            family_email = vals.pop('family_email',False)
            family_mobile = vals.pop('family_mobile',False)
            family_address = vals.pop('family_address',False)
            kinship_id = vals.pop('kinship_id',False)
            auth_level_ids = vals.pop('auth_level_ids', False)
            is_contractor = vals.pop('is_contractor',False)

            ResidentFamily = self.env['resident.family'].sudo()
            family = ResidentFamily.create({
                'name': family_name,
                'phone': family_phone if family_phone else False,
                'image_1920' : family_image_1920 if self.family_image_1920 else False,
                'email' : family_email if family_email else False,
                'mobile' : family_mobile if family_mobile else False,
                'address' : family_address if family_address else False,   
            })
        
            if family:
                RelationshipResidentFamily = self.env['relationship.resident.family'].sudo()
                RelationshipResidentFamily.create({
                    'family_id' : family.id,
                    'resident_id' : record.id,
                    'kinship_id' : kinship_id,
                    'auth_level_ids' : auth_level_ids,
                    'is_contractor' : is_contractor,
                })

        return record

    def write(self, vals):

        if not vals.get('active'):
            for record in self:
               if not record.active:
                    raise UserError(f"No se puede modificar el residente {record.name} por estar inactivo")

        if vals.get('name'):
            for record in self:
                self._check_unique_name(vals['name'], record.id)
        return super().write(vals)

    def get_days_since_registration(self):
        """
        Retorna la cantidad de días que han pasado desde el registro del residente
        Retorna 0 si no hay fecha de creación
        
        Uso:
            resident_obj.get_days_since_registration()
        """
        self.ensure_one()  # Asegura que sea un solo registro
        if self.partner_id.create_date:
            today = date.today()
            # Convertir create_date a date (sin hora)
            create_date = self.partner_id.create_date.date()
            # Calcular diferencia
            delta = today - create_date
            return delta.days
        return 0
    
    def get_days_since_registration_all(self):
        """
        Versión para múltiples registros
        Retorna un diccionario con {resident_id: dias}
        
        Uso:
            resident_objs.get_days_since_registration_all()
        """
        result = {}
        today = date.today()
        
        for resident in self:
            if resident.partner_id.create_date:
                create_date = resident.partner_id.create_date.date()
                delta = today - create_date
                result[resident.id] = delta.days
            else:
                result[resident.id] = 0
        return result

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




