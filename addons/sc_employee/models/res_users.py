import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied

_logger = logging.getLogger(__name__)

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
    group_names = fields.Char(
        string='Nombres de grupo',
        compute='_compute_group_names',
        store=True,
        index=True
    )
    residence_name = fields.Char(
        string='Residencia asignada',
        compute='_compute_residence_name',
        store=False
    ) 

    @api.depends('groups_id.name')
    def _compute_group_names(self):
        for user in self:
            names = user.groups_id.mapped('name')
            user.group_names = ', '.join(names) if names else ''

    @api.depends('employee_id','employee_id.residence_id')
    def _compute_residence_name(self):
        for user in self:
            if user.employee_id:
                if user.employee_id.residence_id:
                    user.residence_name = user.employee_id.residence_id.name
                else:
                    user.residence_name = 'Sin residencia asignada'
            else:
                user.residence_name = 'No es empledado'

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

        old_values = {}
        fields_to_check = list(values.keys())
    
        for record in self:
            old_values[record.id] = {}
            for field in fields_to_check:
                if field in record._fields and record._fields[field].store:
                    field_type = record._fields[field].type
                    try:
                        # Para campos relacionales, guardar solo los IDs
                        if field_type in ['many2many', 'one2many']:
                            old_values[record.id][field] = record[field].ids
                        elif field_type == 'many2one':
                            old_values[record.id][field] = record[field].id if record[field] else False
                        else:
                            old_values[record.id][field] = record[field]
                    except (AccessDenied, ValueError):
                        old_values[record.id][field] = "****** (Acceso denegado)"

        res = super(ResUser, self).write(values)

        model_id = self.env['ir.model']._get('res.users').id
        AuditLog = self.env['audit.log'].sudo()

        for record in self:
            changes = []
            rid = record.id
    
            for field, new_value in values.items():
                if field not in record._fields or not record._fields[field].store:
                    continue
            
                old_val = old_values.get(rid, {}).get(field)
                current_val = new_value
                field_type = record._fields[field].type

                # Manejo especial para campos relacionales
                if field_type in ['many2many', 'one2many']:
                    # Convertir nuevo valor a lista de IDs
                    new_ids = set()
                    for command in new_value:
                        if command[0] == 6:
                            new_ids = set(command[2])
                        elif command[0] == 4:
                            new_ids.add(command[1])
                        elif command[0] == 3:
                            if command[1] in new_ids:
                                new_ids.remove(command[1])
                        # Agregar otros comandos si son necesarios
                
                    # Comparar conjuntos de IDs
                    if set(old_val) != new_ids:
                        changes.append(
                            f"Campo: {field}\n"
                            f"Valor anterior: {old_val}\n"
                            f"Nuevo valor: {list(new_ids)}"
                        )
                    continue
                    
                # Manejo especial para campos sensibles
                if field == 'password':
                    old_val = "********" if old_val else ""
                    current_val = "********"
                elif record._fields[field].type == 'binary':
                    old_val = "** BINARY DATA **" if old_val else ""
                    current_val = "** BINARY DATA **"
        
                # Solo registrar si hubo cambio real
                if old_val != current_val:
                    changes.append(
                        f"Campo: {field}\n"
                        f"Valor anterior: {old_val}\n"
                        f"Nuevo valor: {current_val}"
                      )
    
            if changes:
                AuditLog.create({
                    'name': f"Modificación de usuario {record.login}",
                    'user_id': self.env.user.id,
                    'model_id': model_id,
                    'record_id': rid,
                    'action_type': 'write',
                    'details': "\n\n".join(changes),
                })

        return res

    def unlink(self):
        return self.action_soft_delete()

     

    
    