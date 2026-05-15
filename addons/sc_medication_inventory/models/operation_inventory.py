from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

import logging
import re

_logger = logging.getLogger(__name__)


class OperationInventory(models.Model):
    _name = "operation.inventory"
    _description = "Operación en el Inventario de Medicamentos"
    _order = "date desc"

    quantity = fields.Float(string="Cantidad", required=True)
    uom_id = fields.Many2one("uom.uom", string="Unidad de Medida", required=True)
    reason = fields.Text(string="Motivo de la operación", required=True)
    operation_type = fields.Selection(
        [("in", "Entrada"), ("out", "Salida"), ("adjust", "Ajuste")],
        string="Tipo de Operación",
        required=True,
    )
    user_id = fields.Many2one(
        "res.users",
        string="Registrado por",
        default=lambda self: self.env.user,
        required=True,
        ondelete="restrict",
    )
    medication_inventory_id = fields.Many2one(
        string="Inventario", comodel_name="medication.inventory", ondelete="restrict"
    )
    medication_id = fields.Many2one(
        related="medication_inventory_id.medicament_id",
        string="Medicamento",
    )
    pharmaceutical_form = fields.Char(
        related="medication_inventory_id.pharmaceutical_form",
        string="Forma farmaceutica",
    )
    resident_id = fields.Many2one(
        related="medication_inventory_id.resident_id", string="Residente"
    )
    residence_id = fields.Many2one(
        related="resident_id.residence_id", string="Residencia"
    )
    quantity_str = fields.Char(
        string="Cantidad",
        compute="_compute_quantity_str",
        store=True,
    )
    family_id = fields.Many2one(
        "resident.family",
        string="Familiar",
        ondelete="restrict",
        domain="[('id', 'in', available_family_ids)]",
    )
    date = fields.Datetime(
        string="Fecha/Hora", default=fields.Datetime.now, required=True
    )
    available_family_ids = fields.Many2many(
        "resident.family",
        compute="_compute_available_family_ids",
        string="Familiares disponibles",
    )
    indication_medication_id = fields.Many2one(
        "medical.medication",
        string="Indicación Médica asociada",
    )

    @api.constrains("indication_medication_id", "operation_type", "date")
    def _check_operation_interval(self):
        """Valida que no haya operaciones 'out' muy seguidas para la misma indicación médica."""
        for record in self:
            if record.operation_type == "out" and record.indication_medication_id:
                last_operation = self.search(
                    [
                        (
                            "indication_medication_id",
                            "=",
                            record.indication_medication_id.id,
                        ),
                        ("operation_type", "=", "out"),
                        ("id", "!=", record.id),  # Excluir el registro actual
                    ],
                    order="date desc",
                    limit=1,
                )

                if last_operation:
                    medication = record.indication_medication_id
                    frequency_amount = medication.frequency_amount
                    frequency_unit = medication.frequency_unit

                    if frequency_unit and frequency_amount > 0:
                        period_hours = self._convert_to_hours(
                            frequency_amount, frequency_unit
                        )
                        time_diff = record.date - last_operation.date
                        diff_hours = time_diff.total_seconds() / 3600.0

                        if diff_hours < period_hours:
                            period_str = f"{frequency_amount} {frequency_unit.name}"
                            last_time_str = fields.Datetime.context_timestamp(
                                self, last_operation.date
                            )
                            min_next_time = last_operation.date + timedelta(
                                hours=period_hours
                            )
                            min_next_str = fields.Datetime.context_timestamp(
                                self, min_next_time
                            )

                            raise ValidationError(
                                _(
                                    "No se puede registrar esta operación de salida del inventario. El último suministro de medicamento al residente para esta indicación médica "
                                    "fue el %(last_date)s. El período mínimo entre salidas es de %(period)s "
                                    "(aproximadamente %(hours).1f horas). La próxima salida puede registrarse a partir del %(next_date)s."
                                )
                                % {
                                    "last_date": last_time_str,
                                    "period": period_str,
                                    "hours": period_hours,
                                    "next_date": min_next_str,
                                }
                            )

    def _convert_to_hours(self, amount, uom):
        """Convierte una cantidad y unidad de medida a horas."""
        # Mapeo de unidades de tiempo comunes a horas
        time_conversion = {
            # Minutos
            'minute': 1/60.0,       # minuto
            'minutes': 1/60.0,      # minutos
            'min': 1/60.0,          # min
            'minuto': 1/60.0,       # minuto (español)
            'minutos': 1/60.0,      # minutos (español)
            
            # Horas
            'hour': 1.0,            # hora
            'hours': 1.0,           # horas
            'hr': 1.0,              # hr
            'hora': 1.0,            # hora (español)
            'horas': 1.0,           # horas (español)
            'h': 1.0,               # h
            
            # Días
            'day': 24.0,            # día
            'days': 24.0,           # días
            'día': 24.0,            # día (español)
            'días': 24.0,           # días (español)
            'd': 24.0,              # d
            
            # Semanas
            'week': 168.0,          # semana (7 días)
            'weeks': 168.0,         # semanas
            'semana': 168.0,        # semana (español)
            'semanas': 168.0,       # semanas (español)
            'wk': 168.0,            # wk
            'w': 168.0,             # w
            
            # Meses (aproximado a 30.42 días = 730 horas)
            'month': 730.0,         # mes
            'months': 730.0,        # meses
            'mes': 730.0,           # mes (español)
            'meses': 730.0,         # meses (español)
            'mo': 730.0,            # mo
            
            # Años (aproximado a 365 días = 8760 horas)
            'year': 8760.0,         # año
            'years': 8760.0,        # años
            'yr': 8760.0,           # yr
            'y': 8760.0,            # y
            'año': 8760.0,          # año (español)
            'años': 8760.0,         # años (español)
            'anio': 8760.0,         # año (alternativo)
            'anios': 8760.0,        # años (alternativo)
        }
        
        # Si uom es None, retornar 0
        if not uom:
            return 0.0
        
        # Normalizar el nombre de la unidad
        if hasattr(uom, 'name'):
            unit_name = uom.name.lower().strip()
        else:
            # Si uom es un string, usarlo directamente
            unit_name = str(uom).lower().strip()
        
        # Verificar si la unidad está en el mapeo
        if unit_name in time_conversion:
            return amount * time_conversion[unit_name]
        
        # Si no está en el mapeo, verificar si es una unidad de medida de Odoo
        elif hasattr(uom, 'uom_type'):
            if uom.uom_type == 'bigger':
                # Para unidades mayores (como año a día, día a hora, etc.)
                # Usar factor_inv para convertir a la unidad base (normalmente horas)
                factor = uom.factor_inv if uom.factor_inv != 0 else 1.0
                return amount * factor
                
            elif uom.uom_type == 'smaller':
                # Para unidades menores (como minutos a hora)
                # Usar factor para convertir a la unidad base
                factor = uom.factor if uom.factor != 0 else 1.0
                return amount * factor
                
            elif uom.uom_type == 'reference':
                # Unidad de referencia (normalmente horas)
                return amount
        
        # Verificar si la unidad contiene palabras clave
        for key in time_conversion.keys():
            if key in unit_name:
                return amount * time_conversion[key]
        
        # Si no se puede determinar, intentar usar la categoría
        if hasattr(uom, 'category_id'):
            # Verificar si es categoría de tiempo
            if uom.category_id.name.lower() in ['tiempo', 'time', 'unidades de tiempo']:
                # Intentar deducir por el nombre
                if any(word in unit_name for word in ['year', 'año', 'anio']):
                    return amount * 8760.0  # Año
                elif any(word in unit_name for word in ['month', 'mes']):
                    return amount * 730.0   # Mes
                elif any(word in unit_name for word in ['week', 'semana']):
                    return amount * 168.0   # Semana
                elif any(word in unit_name for word in ['day', 'día', 'dia']):
                    return amount * 24.0    # Día
                elif any(word in unit_name for word in ['hour', 'hora']):
                    return amount * 1.0     # Hora
                elif any(word in unit_name for word in ['minute', 'minuto']):
                    return amount * (1/60.0)  # Minuto
        
        # Valor por defecto: asumir días
        print(f"⚠️ Unidad de tiempo no reconocida: {unit_name}. Usando conversión por defecto (días).")
        return amount * 24.0

    @api.depends("resident_id")
    def _compute_available_family_ids(self):
        for oper in self:
            if oper.resident_id:
                relationships = (
                    self.env["relationship.resident.family"]
                    .sudo()
                    .search([("resident_id", "=", oper.resident_id.id)])
                )
                oper.available_family_ids = relationships.mapped("family_id")
            else:
                oper.available_family_ids = False

    @api.depends("operation_type", "create_date", "medication_inventory_id")
    def _compute_display_name(self):
        selection_dict = dict(self._fields["operation_type"].selection)
        for r in self:
            type_label = selection_dict.get(r.operation_type, "")
            date = r.create_date.strftime("%Y-%m-%d %H:%M")
            r.display_name = (
                f"[{date} - {type_label} - {r.medication_inventory_id.display_name}]"
            )

    @api.depends("quantity", "uom_id")
    def _compute_quantity_str(self):
        for record in self:
            if record.quantity and record.uom_id:
                record.quantity_str = f"{record.quantity} {record.uom_id.name}"

    def _convert_to_iso(self, odoo_datetime):
        """Convierte datetime de Odoo a string ISO 8601"""
        if not odoo_datetime:
            return None

        # Si es un string (formato Odoo), convertir primero a objeto datetime
        if isinstance(odoo_datetime, str):
            dt_obj = fields.Datetime.from_string(odoo_datetime)
        else:  # Ya es un objeto datetime
            dt_obj = odoo_datetime

        return dt_obj.isoformat() + "Z"  # Añadir 'Z' para indicar UTC
    
    @api.model
    def create(self, vals):
        """Sobreescribir create para validar antes de crear el registro."""
        records = super().create(vals)
        # Crear log de auditoría para cada registro creado
        for record in records:
            self.env['audit.log'].sudo().crud_audit_log(record, 'operation.inventory', 'create')
        return records
    
    def write(self, vals):
        """Sobreescribir write para validar antes de actualizar el registro."""
        relevant_fields = {'indication_medication_id', 'operation_type', 'create_date'}
        if any(field in vals for field in relevant_fields):
            for record in self:
                temp_vals = record.copy_data()[0]
                temp_vals.update(vals)
                temp_record = self.new(temp_vals)
                temp_record._check_operation_interval()
        
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
            self.env['audit.log'].sudo().crud_audit_log(record, 'operation.inventory', 'write', extra_details=details)
        return result
    
    def unlink(self):
        # Antes de eliminar, crear logs para cada registro
        for record in self:
            self.env['audit.log'].sudo().crud_audit_log(record, 'operation.inventory', 'unlink')
        return super().unlink()
