from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class Employee(models.Model):
    _inherit = 'hr.employee'

    residence_id = fields.Many2one(
        'residence_house',
        string='Residencia asignada',
        tracking=True,
        help='Casa de residencia donde el empleado está asignado',
        domain="[('active', '=', True)]"
    )
    
    alternative_residences_ids = fields.Many2many(
        'residence_house',
        string='Residencias accesibles',
        relation='employee_alternative_residences_rel',  # AÑADIDO
        column1='employee_id',
        column2='residence_id',
        help='Residencias alternativas donde el empleado puede trabajar',
        domain="[('active', '=', True)]"
    )

    residence_display = fields.Char(
        string="Residencia",
        compute='_compute_residence_display',
        store=True,  
        index=True   
    )
    is_employee_sc = fields.Boolean("Es trabajador de Serena Care", default=False)

    @api.depends('residence_id', 'residence_id.name')
    def _compute_residence_display(self):
        for employee in self:
            employee.residence_display = employee.residence_id.name or "Sin asignación"

    @api.constrains('residence_id', 'alternative_residences_ids')
    def _check_residence_in_alternatives(self):
        for employee in self:
            if employee.residence_id and employee.alternative_residences_ids:
                if employee.residence_id not in employee.alternative_residences_ids:
                    raise ValidationError(
                        _('La residencia asignada debe estar en la lista de residencias alternativas.')
                    )

    @api.constrains('residence_id')
    def _check_residence_active(self):
        for employee in self:
            if employee.residence_id and not employee.residence_id.active:
                raise ValidationError(
                    _('No se puede asignar un empleado a una residencia inactiva.')
                )

    @api.model
    def create(self, values):

        # Validación de residencia
        if values.get('residence_id') and values.get('alternative_residences_ids'):
            alt_residences = values['alternative_residences_ids'][0][2]
            if values['residence_id'] not in alt_residences:
                raise ValidationError(
                    _('La residencia asignada debe estar en la lista de residencias accesibles.')
                )

        current_context = self.env.context 
        if 'user_serena_care' in current_context or 'employee_serena_care' in current_context:
            values['is_employee_sc'] = True
        result = super().create(values)
        return result

    
    def write(self, values):
        # Validación de residencia
        if 'residence_id' in values or 'alternative_residences_ids' in values:
            self._validate_residence_update(values)

        current_context = self.env.context 
        if 'user_serena_care' in current_context or 'employee_serena_care' in current_context:
            values['is_employee_sc'] = True
        res = super().write(values)
        return res 

    def _validate_residence_update(self, vals):
        for employee in self:
            new_residence = vals.get('residence_id', employee.residence_id.id)
            new_alternatives = vals.get('alternative_residences_ids') or employee.alternative_residences_ids.ids
            
            if 'alternative_residences_ids' in vals:
                if vals['alternative_residences_ids']:
                    command_list = vals['alternative_residences_ids']
                    new_alt_ids = set(employee.alternative_residences_ids.ids)
                    for command in command_list:
                        if command[0] == 6:
                            new_alt_ids = set(command[2])
                        elif command[0] in (3, 2):
                            new_alt_ids.discard(command[1])
                        elif command[0] == 4:
                            new_alt_ids.add(command[1])
                        elif command[0] == 5:
                            new_alt_ids = set()
                    new_alternatives = list(new_alt_ids)
                else:
                    new_alternatives = []
            
            if new_residence and new_alternatives:
                if new_residence not in new_alternatives:
                    raise ValidationError(
                        _('La residencia asignada debe estar en la lista de residencias accesibles.')
                    )

    # has_user = fields.Boolean(compute='_compute_has_user')
    
    # # Campos relacionados editables para sincronización con usuario
    # login = fields.Char(
    #     string="Usuario (Temporal)",
    #     help="Solo para creación inicial",
    #     transient=True
    # )
    # password = fields.Char(
    #     string="Contraseña (Temporal)",
    #     transient=True
    # )
    
    # # Mantener campos sincronizados
    # user_login = fields.Char(
    #     string="Usuario",
    #     related='user_id.login',
    #     store=True,
    #     readonly=False
    # )
    # 
    
    # is_carer = fields.Boolean(
    #     string = "Cuidador",
    #     transient = True,
    #     help = "Indica si el empleado tiene el rol de cuidador",
    # )
    # is_admin = fields.Boolean(
    #     string = "Administrador",
    #     transient = True,
    #     help = "Indica si el empleado tiene el rol de administrador",
    # )
    # is_doctor = fields.Boolean(
    #     string = "Doctor",
    #     transient = True,
    #     help = "Indica si el empleado tiene el rol de doctor",
    # )
    # is_nurse = fields.Boolean(
    #     string = "Enfermera",
    #     transient = True,
    #     help = "Indica si el empleado tiene el rol de enfermera",
    # ) 

    # # ========== COMPUTE/INVERSE METHODS ==========
    
    
    # @api.depends('user_id')
    # def _compute_has_user(self):
    #     for employee in self:
    #         employee.has_user = bool(employee.user_id)
    


    # # ========== CONSTRAINTS/VALIDATIONS ==========
    
    

    
    
    # @api.constrains('user_id')
    # def _check_user_employee_link(self):
    #     for employee in self:
    #         if employee.user_id and employee.user_id.employee_id != employee:
    #             raise ValidationError(_(
    #                 "El usuario asociado ya está vinculado a otro empleado"
    #             ))
    
    # @api.constrains('login')
    # def _check_valid_login(self):
    #     for employee in self:
    #         if employee.login:
    #             if not employee.login.strip():
    #                 raise ValidationError(_("El nombre de usuario no puede estar vacío"))
    #             if not employee.login.isidentifier():
    #                 raise ValidationError(_(
    #                     f"El nombre de usuario solo puede contener letras, números y guiones bajos: {employee.login}"
    #                 ))

    # # ========== CRUD METHODS ==========
    
    # @api.model
    # def create(self, vals):
    #     # Extraer credenciales temporales
    #     login = vals.pop('login', None)
    #     password = vals.pop('password', None)
        
    #     
        
    #     # Validar credenciales
    #     if login:
    #         if not login.strip():
    #             raise ValidationError(_("El nombre de usuario no puede estar vacío"))
    #         if not login.isidentifier():
    #             raise ValidationError(_(
    #                 f"El nombre de usuario solo puede contener letras, números y guiones bajos :{login}"
    #             ))
    #         if not password:
    #             raise ValidationError(_("Debe proporcionar una contraseña"))
        
    #     # Crear empleado
    #     vals['is_worker_sc']  = True
    #     employee = super().create(vals)
        
    #     # Crear usuario si hay credenciales
    #     if login and password:
    #         try:
    #             # Manejar grupos
    #             group_ids = []
                
    #             # Asegurar grupo base
    #             base_group = self.env.ref('base.group_user')
    #             base_group_serena = self.env.ref('sc_group.group_residence_user')
                
    #             # Grupos de Serena-Care
    #             group_sc_carer = self.env.ref('sc_group.group_carer')
    #             group_sc_admin = self.env.ref('sc_group.group_residence_manager')
    #             group_sc_doctor = self.env.ref('sc_group.group_doctor')
    #             group_sc_nurse = self.env.ref('sc_group.group_nurse')      
   
    #             is_carer = vals.pop('is_carer', False)
    #             is_admin = vals.pop('is_admin', False)
    #             is_doctor = vals.pop('is_doctor', False)      
    #             is_nurse = vals.pop('is_nurse', False)      
                      

    #             if base_group and base_group.id not in group_ids:
    #                 group_ids.append(base_group.id)
                
    #             if base_group_serena and base_group_serena.id not in group_ids:
    #                 group_ids.append(base_group_serena.id)   

    #             if is_admin and group_sc_admin and group_sc_admin.id not in group_ids:
    #                 group_ids.append(group_sc_admin.id)

    #             if is_carer and group_sc_carer and group_sc_carer.id not in group_ids:
    #                 group_ids.append(group_sc_carer.id)

    #             if is_doctor and group_sc_doctor and group_sc_doctor.id not in group_ids:
    #                 group_ids.append(group_sc_doctor.id)

    #             if is_nurse and group_sc_nurse and group_sc_nurse.id not in group_ids:
    #                 group_ids.append(group_sc_nurse.id) 

    #             # Crear usuario
    #             user_vals = {
    #                 'name': employee.name,
    #                 'login': login,
    #                 'password': password,
    #                 'groups_id': [(6, 0, group_ids)],
    #                 'image_1920': employee.image_1920,
    #                 'email': vals.get('email'),
    #                 'is_user_sc': True,
    #                 'partner_id': employee.user_partner_id.id 
    #             }
                
    #             user = self.env['res.users'].with_context(
    #                 no_reset_password=True
    #             ).create(user_vals)
                
    #             # Vincular usuario y empleado
    #             employee.write({'user_id': user.id})
                
    #         except Exception as e:
    #             _logger.error("Error creando usuario: %s", e)
    #             raise ValidationError(_("Error creando usuario: %s") % str(e))
        
    #     return employee

    # def write(self, vals):
    #     # Evitar recursión usando bandera en el contexto
    #     # if self.env.context.get('skip_employee_update'):
    #     #     return super().write(vals)
        
    #     
        
    #     # Preparar valores para usuario
    #     # user_vals = {}
    #     # if 'name' in vals:
    #     #     user_vals['name'] = vals['name']
    #     # if 'image_1920' in vals:
    #     #     user_vals['image_1920'] = vals['image_1920']
        
    #     # # Actualizar usuario asociado con bandera anti-recursión
    #     # for employee in self:
    #     #     if user_vals and employee.user_id:
    #     #         employee.user_id.with_context(
    #     #             skip_user_update=True
    #     #         ).write(user_vals)
        
    #     return super().write(vals)
    
    # def unlink(self):
    #     users = self.mapped('user_id')
    #     res = super().unlink()
    #     users.unlink()
    #     return res

    # # ========== HELPER METHODS ==========
    
    # 
    
    # @api.onchange('residence_id')
    # def _onchange_residence_id(self):
    #     if self.residence_id and hasattr(self.residence_id, 'partner_id'):
    #         self.work_location_id = self.residence_id.partner_id.id