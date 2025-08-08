from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied


class ResUser(models.Model):
    _inherit = 'res.users'  # Solo hereda de res.users
    
    
    is_user_sc = fields.Boolean(
        string="Es usuario de Serena Care", 
        default=False,
    )
    is_employee_sc = fields.Boolean(
        string="Trabaja en alguna residencia", 
        default=False,
        transient=True,
    )

    @api.model
    def create(self, vals):
        login = vals.get('login', None)
        password = vals.get('password', None)
        confirmed_password = vals.pop('confirmed_password', None)
        is_employee_sc = vals.pop('is_employee_sc', False)

        if login:
            if not login.strip():
                raise ValidationError(_("El nombre de usuario no puede estar vacío"))
            if not login.isidentifier():
                raise ValidationError(_(
                    f"El nombre de usuario solo puede contener letras, números y guiones bajos: {login}"
                ))

        if not password:
           raise ValidationError("Debe proporcionar una contraseña")

        if not confirmed_password or confirmed_password != password:
           raise ValidationError("Las contraseñas no coinciden")
        
        # Asegurar grupos base
        base_group = self.env.ref('base.group_user')
        base_group_serena = self.env.ref('sc_group.group_residence_user')

        groups_id = vals.get('groups_id', [])
        if groups_id:
            groups_id = groups_id[0][2] if groups_id[0][0] == 6 else groups_id
        else:
            groups_id = []
            
        if base_group and base_group.id not in groups_id:
            groups_id.append(base_group.id)
        if base_group_serena and base_group_serena.id not in groups_id:
            groups_id.append(base_group_serena.id)
            
        vals['groups_id'] = [(6, 0, groups_id)]

        current_context = self.env.context 
        if 'user_serena_care' in current_context:
            vals['is_user_sc'] = True     
        
        user = super(ResUser, self).create(vals)
        if is_employee_sc:
            user.with_context(
                user_serena_care=True,
                employee_serena_care=True,
            ).action_create_employee()
        return user

    def write(self, values):
        current_context = self.env.context 
        if 'user_serena_care' in current_context:
            values['is_user_sc'] = True 

        if 'password' in values:
            password = values['password']
            confirmed_password = values.pop('confirmed_password', None)
            
            if not password:
                raise ValidationError(_("La contraseña no puede estar vacía"))
                
            if not confirmed_password or confirmed_password != password:
                raise ValidationError(_("Las contraseñas no coinciden"))
                
        return super(ResUser, self).write(values)

    def unlink(self):
        return self.action_soft_delete()

    def toggle_active_state(self):
        for user in self:
            user.active = not user.active
        return True

    
    