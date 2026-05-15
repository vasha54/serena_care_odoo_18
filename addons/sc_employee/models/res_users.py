import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied

_logger = logging.getLogger(__name__)


class ResUser(models.Model):
    _inherit = "res.users"  # Solo hereda de res.users

    is_employee_sc = fields.Boolean(
        string="Trabaja en alguna residencia",
        default=False,
        transient=True,
    )
    group_names = fields.Char(
        string="Nombres de grupo",
        compute="_compute_group_names",
        store=True,
        index=True,
    )
    residence_name = fields.Char(
        string="Residencia asignada", compute="_compute_residence_name", store=False
    )
    
    accessible_residences_ids = fields.Many2many(
        'residence_house',
        string='Residencias accesibles',
        compute='_compute_accessible_residences',
        store=False,
        help='Residencias a las que el usuario tiene acceso'
    )
    
    selected_residences_ids = fields.Many2many(
        'residence_house',
        string='Residencias seleccionadas',
        domain="[('id', 'in', accessible_residences_ids)]",
        help='Residencias seleccionadas para operar actualmente',
        default=lambda self: self._default_selected_residences()
    )
    
    @api.depends('employee_ids', 'employee_ids.residence_id', 
                 'employee_ids.alternative_residences_ids', 'groups_id',
                 'employee_id', 'employee_id.residence_id',
                 'employee_id.alternative_residences_ids')
    def _compute_accessible_residences(self):
        """Calcula las residencias accesibles para el usuario"""
        for user in self:
            residences = self.env['residence_house'].sudo()
            
            # Si el usuario pertenece al grupo Admin, tiene acceso a todas las residencias activas
            if user.has_group('sc_group.gs_admin'):
                residences = self.env['residence_house'].sudo().search([('active', '=', True),('is_deleted','=',False)])
            else:
                # Obtener residencias del empleado
                if user.employee_id:
                    employee = user.employee_id
                    if employee.residence_id:
                        residences += employee.residence_id
                    residences += employee.alternative_residences_ids
                # Eliminar duplicados y aplicar dominio de activas
                residences = residences.filtered(lambda r: r.active and not r.is_deleted)
            
            user.accessible_residences_ids = residences
    
    def _default_selected_residences(self):
        """Obtiene las residencias por defecto"""
        #self.ensure_one()
        accessible = self.accessible_residences_ids
        
        # Si el usuario tiene una sola residencia accesible, seleccionarla por defecto
        if len(accessible) == 1:
            return [(6, 0, [accessible.id])]
        return False
    
    @api.constrains('selected_residences_ids')
    def _check_selected_residences(self):
        """Valida que las residencias seleccionadas estén entre las accesibles"""
        for user in self:
            if not user.has_group('module_category_serena.gs_admin'):
                invalid_residences = user.selected_residences_ids - user.accessible_residences_ids
                if invalid_residences:
                    raise ValidationError(
                        _('Las siguientes residencias seleccionadas no están entre las accesibles: %s') %
                        ', '.join(invalid_residences.mapped('name'))
                    )

    @api.depends("groups_id.name")
    def _compute_group_names(self):
        for user in self:
            names = user.groups_id.mapped("name")
            user.group_names = ", ".join(names) if names else ""

    @api.depends("employee_id", "employee_id.residence_id")
    def _compute_residence_name(self):
        for user in self:
            if user.employee_id:
                if user.employee_id.residence_id:
                    user.residence_name = user.employee_id.residence_id.name
                else:
                    user.residence_name = "Sin residencia asignada"
            else:
                user.residence_name = "No es empledado"

    @api.model
    def create(self, vals):
        login = vals.get("login", None)
        password = vals.get("password", None)
        confirmed_password = vals.pop("confirmed_password", None)
        is_employee_sc = vals.pop("is_employee_sc", False)

        if login:
            if not login.strip():
                raise ValidationError(_("El nombre de usuario no puede estar vacío"))
            if not login.isidentifier():
                raise ValidationError(
                    _(
                        f"El nombre de usuario solo puede contener letras, números y guiones bajos: {login}"
                    )
                )

        if not password:
            raise ValidationError("Debe proporcionar una contraseña")

        if not confirmed_password or confirmed_password != password:
            raise ValidationError("Las contraseñas no coinciden")

        # Asegurar grupos base
        base_group = self.env.ref("base.group_user")
        base_group_serena = self.env.ref("sc_group.gs_user")

        groups_id = vals.get("serena_group_ids", [])

        # Manejar diferentes formatos de groups_id
        group_ids_to_set = []

        if groups_id:
            # Si groups_id es una lista de comandos Odoo (como [(4, ref('sc_group.gs_user'))])
            if (
                isinstance(groups_id, list)
                and groups_id
                and isinstance(groups_id[0], (list, tuple))
            ):
                # Extraer IDs de los comandos (4, id) y (6, 0, [ids])
                for command in groups_id:
                    if command[0] == 4:  # Comando (4, id) - añadir
                        group_ids_to_set.append(command[1])
                    elif command[0] == 6:  # Comando (6, 0, [ids]) - reemplazar
                        if len(command) > 2:
                            group_ids_to_set.extend(command[2])
                    elif command[0] == 3:  # Comando (3, id) - eliminar
                        # Ignorar para creación
                        pass
            else:
                # Si ya es una lista de IDs
                group_ids_to_set = (
                    groups_id if isinstance(groups_id, list) else [groups_id]
                )

        # Asegurar que los grupos base estén incluidos
        if base_group and base_group.id not in group_ids_to_set:
            group_ids_to_set.append(base_group.id)
        if base_group_serena and base_group_serena.id not in group_ids_to_set:
            group_ids_to_set.append(base_group_serena.id)

        # Establecer los grupos usando comando (6, 0, [ids]) para reemplazar
        vals["groups_id"] = [(6, 0, list(set(group_ids_to_set)))]

        # Para usuarios creados desde datos XML, establecer el contexto apropiado
        current_context = self.env.context
        if "from_xml_data" in current_context or "install_mode" in current_context:
            vals["is_user_sc"] = True
        if "user_serena_care" in current_context:
            vals["is_user_sc"] = True

        # Llamar al create original
        user = super().create(vals)
        # Solo crear empleado si es necesario y no estamos en modo instalación
        if is_employee_sc and "install_mode" not in self.env.context:
            user.with_context(
                user_serena_care=True,
                employee_serena_care=True,
            ).action_create_employee()
            
        user._compute_accessible_residences()
        
        return user

    def write(self, values):
        current_context = self.env.context
        if "user_serena_care" in current_context:
            values["is_user_sc"] = True

        if "password" in values:
            password = values["password"]
            confirmed_password = values.pop("confirmed_password", None)

            if not password:
                raise ValidationError(_("La contraseña no puede estar vacía"))

            if not confirmed_password or confirmed_password != password:
                raise ValidationError(_("Las contraseñas no coinciden"))

        if "serena_group_ids" in values:
            values["groups_id"] = values.pop("serena_group_ids",[])

        old_values = {}
        fields_to_check = list(values.keys())

        for record in self:
            old_values[record.id] = {}
            for field in fields_to_check:
                if field in record._fields and record._fields[field].store:
                    field_type = record._fields[field].type
                    try:
                        # Para campos relacionales, guardar solo los IDs
                        if field_type in ["many2many", "one2many"]:
                            old_values[record.id][field] = record[field].ids
                        elif field_type == "many2one":
                            old_values[record.id][field] = (
                                record[field].id if record[field] else False
                            )
                        else:
                            old_values[record.id][field] = record[field]
                    except (AccessDenied, ValueError):
                        old_values[record.id][field] = "****** (Acceso denegado)"

        res = super().write(values)
        
        # Recalcular si cambió algo que afecta las residencias accesibles
        fields_to_check = ['groups_id', 'employee_ids']
        if any(field in values for field in fields_to_check):
            self._compute_accessible_residences()

        model_id = self.env["ir.model"]._get("res.users").id
        AuditLog = self.env["audit.log"].sudo()

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
                if field_type in ["many2many", "one2many"]:
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
                if field == "password":
                    old_val = "********" if old_val else ""
                    current_val = "********"
                elif record._fields[field].type == "binary":
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
                AuditLog.create(
                    {
                        "name": f"Modificación de usuario {record.login}",
                        "user_id": self.env.user.id,
                        "model_id": model_id,
                        "record_id": rid,
                        "action_type": "write",
                        "details": "\n\n".join(changes),
                    }
                )

        return res

    def unlink(self):
        if self.employee_id:
            self.employee_id.action_soft_delete()
        return self.action_soft_delete()
    
    def action_restore(self):
        if self.employee_id:
            self.employee_id.action_restore()
        self.write({"is_deleted": False})
        _logger.info(f"Usuario restaurado: ID {self.id}, Login: {self.login}")
        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }