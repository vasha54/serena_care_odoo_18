from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import email_normalize



import logging
import re

_logger = logging.getLogger(__name__)


class MedicationInventory(models.Model):
    _name = "medication.inventory"
    _description = "Inventario de Medicamentos"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    medicament_id = fields.Many2one(
        "medicament.product", string="Medicamento", required=True
    )
    pharmaceutical_form = fields.Char(
        related='medicament_id.pharmaceutical_form',
        readonly=True,
        string='Forma Farmacéutica', 
        required=True, 
        ondelete='restrict',
        tracking=True
    )
    resident_id = fields.Many2one("resident", string="Residente", required=True)
    available_quantity = fields.Float(string="Cantidad Disponible", required=True)
    alert_quantity = fields.Float(
        string="Cantidad de Notificación de Alerta", required=True
    )
    warning_quantity = fields.Float(
        string="Cantidad de Notificación de Advertencia", required=True
    )
    uom_id = fields.Many2one("uom.uom", string="Unidad de Medida", required=True)
    cat_uom_id = fields.Many2one(
        "uom.category", string="Categoría de la unidad de medida", required=True
    )
    residence_id = fields.Many2one(
        related="resident_id.residence_id", string="Residencia"
    )
    quantity_str = fields.Char(
        string="Cantidad Disponible",
        compute="_compute_quantity_str",
        store=True,
    )
    is_alert = fields.Boolean(
        string="Medicamento en Alerta de agotamiento",
        compute="_compute_state",
        store=True,
    )
    is_warning = fields.Boolean(
        string="Medicamento en Advertencia de agotamiento",
        compute="_compute_state",
        store=True,
    )
    reason_inventory = fields.Text(
        string="Motivo de la existencia de este inventario",
    )
    reason_inventory_compute = fields.Text(
        string="Motivo de la existencia de este inventario computado",
        compute="_compute_reason_inventory",
        store=False,
    )
    medical_indication_ids = fields.One2many(
        'medical.medication', 
        'inventory_id',
        string='Indicaciones médicas de medicamento'
    )
    

    # Restricción SQL
    _sql_constraints = [
        (
            "unique_medicament_resident_uom_category_pharmaceutical_form",
            "UNIQUE(medicament_id, resident_id, cat_uom_id, pharmaceutical_form)",
            "Ya existe un registro para este medicamento, forma farmacéutica, residente y categoría de unidad de medida.",
        )
    ] 

    

    @api.depends("available_quantity", "uom_id")
    def _compute_quantity_str(self):
        for record in self:
            if record.available_quantity and record.uom_id:
                record.quantity_str = (
                    f"{record.available_quantity} {record.uom_id.name}"
                )
            if not record.available_quantity and record.uom_id:
                record.quantity_str = (
                    f"0 {record.uom_id.name}"
                )

    @api.depends("alert_quantity", "warning_quantity", "available_quantity")
    def _compute_state(self):
        for record in self:
            record.is_alert = False
            record.is_warning = False
            if (
                record.available_quantity <= record.warning_quantity
                and record.available_quantity > record.alert_quantity
            ):
                record.is_warning = True
            elif record.available_quantity <= record.alert_quantity:
                record.is_alert = True

    # Restricción Python
    @api.constrains("medicament_id", "resident_id", "cat_uom_id")
    def _check_unique_triad(self):
        for record in self:
            existing = self.search(
                [
                    ("medicament_id", "=", record.medicament_id.id),
                    ("resident_id", "=", record.resident_id.id),
                    ("cat_uom_id", "=", record.cat_uom_id.id),
                    ("id", "!=", record.id),
                ],
                limit=1,
            )
            if existing:
                raise ValidationError(
                    "Ya existe un registro para este medicamento, residente y categoría de unidad de medida."
                )

    
    @api.depends('medicament_id', 'resident_id', 'pharmaceutical_form', 'uom_id')
    def _compute_display_name(self):
        for r in self:
            r.display_name = f"{r.resident_id.name} - [{r.medicament_id.name}/{r.pharmaceutical_form}/{r.uom_id.name}]"

    @api.depends('medical_indication_ids','reason_inventory')
    def _compute_reason_inventory(self):
        for record in self:
            if not record.medical_indication_ids and not record.reason_inventory:
                record.reason_inventory_compute = "No existen razones para la existencia de este inventario de medicamento"
            elif record.reason_inventory:
                record.reason_inventory_compute = record.reason_inventory
            elif record.medical_indication_ids:
                indications_text = record._generate_medical_indications_text()
                record.reason_inventory_compute = indications_text

    def _format_medical_indication(self, indication):
        """Formatea una indicación médica en formato compacto"""
        # Información esencial
        parts = [
            f"{indication.medicament_id.name}",
            f"{indication.dosage_amount}{indication.dosage_unit.name}",
            f"cada {indication.frequency_amount}{indication.frequency_unit.name}",
            f"vía {indication.route_id.name}"
        ]
        
        # Información del período
        if indication.is_lifetime_medication:
            parts.append("medicación permanente")
        else:
            start = indication.start_date_medication.strftime('%d/%m/%Y') if indication.start_date_medication else "fecha inicio no especificada"
            if indication.end_date_medication:
                end = indication.end_date_medication.strftime('%d/%m/%Y')
                parts.append(f"desde {start} hasta {end}")
            else:
                parts.append(f"desde {start}")
        
        return " • ".join(parts)

    def _generate_medical_indications_text(self):
        """Genera texto con todas las indicaciones médicas"""
        self.ensure_one()
        
        if not self.medical_indication_ids:
            return "No hay indicaciones médicas asociadas"
        
        header = "Indicaciones médicas asociadas:\n"
        indications = []
        
        for i, indication in enumerate(self.medical_indication_ids, 1):
            indication_text = self._format_medical_indication(indication)
            indications.append(f"{i}. {indication_text}")
        
        return header + "\n".join(indications)

    @api.model
    def _notification_status_alert(self):
        inventory_alert = self.search([('is_alert','=',True)]) 
        for inventory in inventory_alert:
            self._notify_by_chat_message(inventory,'alert')
            self._notify_by_email(inventory,'alert')

    @api.model
    def _notification_status_warning(self):
        inventory_warning = self.search([('is_warning','=',True)])
        for inventory in inventory_warning:
            self._notify_by_chat_message(inventory,'warning')
            self._notify_by_email(inventory,'warning')
 
    @api.model
    def _notify_by_email(self,_inventory,_status):
        try:
            recipients = set()

            if not recipients:
                return

            residence = _inventory.residence_id
            employees = residence.employee_ids
            for employee in employees:
                if employee.user_id:
                    user = employee.user_id
                    normalized_email = email_normalize(user.email)
                    if normalized_email:
                        recipients.add(normalized_email)
            
            familys = _inventory.resident_id.family_ids
            for family in familys:
                if family.email:
                    normalized_email = email_normalize(family.email)
                    if normalized_email:
                        recipients.add(normalized_email)

            status = "Advertencia" if _status == 'warning' else "Alerta"

            subject = f"{status} - Agotamiento de medicamento"

            body = _(
                    "Un Inventario de Medicamento ha pasado al estado de: %(status)s\n\n"
                    "Residente: %(resident)s<br/>"
                    "Medicamento: %(medicament)s<br/>"
                    "Forma farmacéutica: %(pharmaceutical_form)s<br/>"
                    "Cantidad disponible: %(quantity)s<br/>"
                    ) % {
                    "status": status,
                    "resident": _inventory.resident_id.name,
                    "medicament": _inventory.medicament_id.name,
                    "pharmaceutical_form": _inventory.pharmaceutical_form,
                    "quantity": _inventory.quantity_str,
                }

            mail_values = {
                "subject": subject,
                "body_html": "<pre>%s</pre>" % body.replace("<br/>","\n"),
                "email_to": ",".join(recipients),
                "auto_delete": True,
                "model": "medication.inventory",
                "res_id": _inventory.id,
            }

            self.env["mail.mail"].create(mail_values).send()
        except Exception as e:
            _logger.error("Chat notification error: %s", str(e), exc_info=True)
   
    @api.model
    def _notify_by_chat_message(self,_inventory,_status):
        try:
            residence = _inventory.residence_id
            employees = residence.employee_ids
            DiscussChannel = self.env["discuss.channel"].sudo()
            status = "Advertencia" if _status == 'warning' else "Alerta"
            for employee in employees:
                if employee.user_id:
                    user = employee.user_id
                    channel = DiscussChannel.create(
                        {
                            "name": f"{status} - Medicamento en Agotamiento",
                            "channel_type": "group",
                        }
                    )
                    partner = user.partner_id
                    channel.sudo().add_members(partner.id)
                    message_body = _(
                                "Estado del Inventario: %(status)s<br/>"
                                "Residente: %(resident)s<br/>"
                                "Medicamento: %(medicament)s<br/>"
                                "Forma farmacéutica: %(pharmaceutical_form)s<br/>"
                                "Cantidad disponible: %(quantity)s<br/>"
                                ) % {
                                    "status": status,
                                    "resident": _inventory.resident_id.name,
                                    "medicament": _inventory.medicament_id.name,
                                    "pharmaceutical_form": _inventory.pharmaceutical_form,
                                    "quantity": _inventory.quantity_str,
                                }
                    # Enviar como OdooBot
                    odoobot = self.env.ref("base.partner_root")
                    channel.sudo().message_post(
                        body=message_body.replace("<br/>","\n"),
                        message_type="comment",
                        subtype_xmlid="mail.mt_comment",
                        author_id=odoobot.id,
                    )
        except Exception as e:
            _logger.error("Chat notification error: %s", str(e), exc_info=True) 
            
    @api.model
    def create(self, values):
        records = super().create(values)
        # Crear log de auditoría para cada registro creado
        for record in records:
            self.env['audit.log'].sudo().crud_audit_log(record, 'medication.inventory', 'create')
        return records
    
    def write(self, vals):
        # Guardar estado anterior para detectar cambios (opcional, mejora la calidad del detalle)
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
            self.env['audit.log'].sudo().crud_audit_log(record, 'medication.inventory', 'write', extra_details=details)
        return result

    def unlink(self):
        # Antes de eliminar, crear logs para cada registro
        for record in self:
            self.env['audit.log'].sudo().crud_audit_log(record, 'medication.inventory', 'unlink')
        return super().unlink()