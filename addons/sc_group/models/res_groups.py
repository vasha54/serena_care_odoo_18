from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError

import logging

_logger = logging.getLogger(__name__)


class ResGroups(models.Model):
    _inherit = ["res.groups"]

    active = fields.Boolean(string="Activo", default=True)
    category_id = fields.Many2one(
        "ir.module.category",
        string="Category",
        default=lambda self: self.env.ref("sc_group.module_category_serena").id,
    )
    is_group_serena = fields.Boolean(
        string="Es grupo de Serena",
        default=False,
    )
    count_users = fields.Integer(
        string="Cantidad de usuarios", compute="_compute_users"
    )
    # can_delete = fields.Boolean(string="Se puede eliminar", default=True)

    @api.depends("users")
    def _compute_users(self):
        for record in self:
            if record.users:
                record.count_users = len(record.users)
            else:
                record.count_users = 0

    @api.model
    def create(self, vals):
        if "name" in vals and vals["name"]:
            existing = self.search([("name", "=", vals["name"])], limit=1)
            if existing:
                raise ValidationError(
                    _("Ya existe un grupo con el nombre '%s'.") % vals["name"]
                )

        current_context = self.env.context
        if current_context.get("group_serena"):
            vals["is_group_serena"] = True

        records = super().create(vals)
        # Crear log de auditoría para cada registro creado
        for record in records:
            self.env['audit.log'].sudo().crud_audit_log(record, 'res.groups', 'create')
        return records

    def write(self, vals):
        if "name" in vals and vals["name"]:
            for record in self:
                existing = self.search(
                    [("name", "=", vals["name"]), ("id", "!=", record.id)], limit=1
                )
                if existing:
                    raise ValidationError(
                        _("Ya existe otro grupo con el nombre '%s'.") % vals["name"]
                    )

        if "active" in vals:
            for record in self:
                if record.active and vals.get("active") is False:
                    record._deactivate_group()
                if (not record.active) and vals.get("active") is True:
                    record._reactivate_group()

        old_values = {}
        for record in self:
            old_values[record.id] = {
                field: record[field] for field in vals if field in record._fields and not record._fields[field].compute
            }
        result = super().write(vals)
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
            self.env['audit.log'].sudo().crud_audit_log(record, 'res.groups', 'write', extra_details=details)
        return result

    def unlink(self):
        for record in self:
            if record.users:
                raise UserError(
                    _(
                        "Este rol no puede eliminarse porque está "
                        "asignado a usuarios activos."
                    )
                )
            # if record.can_delete:
            #     raise UserError(
            #         _("Este Rol no puede eliminarse por ser base del sistema")
            #     )
        # Antes de eliminar, crear logs para cada registro
        for record in self:
            self.env['audit.log'].sudo().crud_audit_log(record, 'res.groups', 'unlink')
        return super().unlink()

    def _deactivate_group(self):
        """Guardar usuarios actuales y desasignarles el grupo para que pierdan permisos."""
        pass
        # for group in self:
        #     if not group.active:
        #         continue
        #     users = group.users.sorted()  # lista de usuarios actuales
        #     if users:
        #         # guardar la lista para posible restauración
        #         group.archived_user_ids = [(6, 0, users.ids)]
        #         # quitar el grupo de esos usuarios
        #         users.write({'groups_id': [(3, group.id)]})
        #         _logger.info("Grupo %s desactivado: desasignado de %s usuarios." % (group.name, len(users)))
        #     # marcar el grupo como inactivo (no usar write que recursaría)
        #     super(ResGroups, group).write({'active': False})

    def _reactivate_group(self):
        """Restaurar usuarios desde archived_user_ids (opcional)."""
        pass
        # for group in self:
        #     if group.active:
        #         continue
        #     # volver a marcar como activo
        #     super(ResGroups, group).write({'active': True})
        #     # restaurar usuarios guardados
        #     if group.archived_user_ids:
        #         # añadir el grupo a los usuarios archivados de nuevo
        #         users_to_restore = group.archived_user_ids
        #         users_to_restore.write({'groups_id': [(4, group.id)]})
        #         # limpiar campo de archive
        #         group.archived_user_ids = [(5,)]
        #         _logger.info("Grupo %s reactivado: restaurado a %s usuarios." % (group.name, len(users_to_restore)))
