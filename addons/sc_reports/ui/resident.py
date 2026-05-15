import logging
from collections import defaultdict
from datetime import datetime, timedelta
from pytz import timezone

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError


_logger = logging.getLogger(__name__)


class Resident(models.Model):
    _inherit = "resident"

    def _convert_timezone_datetime(self, _user, _date):
        """
        Convierte un datetime de UTC a la zona horaria del usuario.

        Args:
            _user: objeto usuario con tz
            _date: objeto datetime (asume que está en UTC)
        """
        _logger.info(f"User tz: {_user.tz}")
        user_tz = timezone(_user.tz or "UTC")
        utc_tz = timezone("UTC")

        # Asegurarnos de que el datetime tenga zona horaria UTC
        if _date.tzinfo is None:
            # Si es naive, asumir que está en UTC y añadir timezone UTC
            utc_dt = utc_tz.localize(_date)
        else:
            # Si ya tiene timezone, convertir a UTC por si acaso
            utc_dt = _date.astimezone(utc_tz)

        # Convertir a la zona del usuario
        user_dt = utc_dt.astimezone(user_tz)

        return user_dt

    def _convert_timezone(self, _user, _date):
        """
        Convierte un datetime de UTC a la zona horaria del usuario.

        Args:
            _user: objeto usuario con tz
            _date: objeto datetime (asume que está en UTC)
        """
        _logger.info(f"User tz: {_user.tz}")
        user_tz = timezone(_user.tz or "UTC")
        utc_tz = timezone("UTC")

        # Asegurarnos de que el datetime tenga zona horaria UTC
        if _date.tzinfo is None:
            # Si es naive, asumir que está en UTC y añadir timezone UTC
            utc_dt = utc_tz.localize(_date)
        else:
            # Si ya tiene timezone, convertir a UTC por si acaso
            utc_dt = _date.astimezone(utc_tz)

        # Convertir a la zona del usuario
        user_dt = utc_dt.astimezone(user_tz)

        return user_dt.strftime("%d/%m/%Y %H:%M:%S")

    def get_medication_operations_summary(self):
        """
        Retorna un diccionario con las operaciones de inventario agrupadas por medicamento,
        ordenadas por fecha descendente.

        Returns:
            dict: Diccionario con estructura {medicamento_id: {'name_medicament': str, 'data_operations': list}}
        """
        self.ensure_one()

        # Diccionario para almacenar los resultados
        operations_by_medication = {}

        # Obtener todos los inventarios de medicamentos del residente
        inventory_ids = self.medication_inventory_ids.ids

        if not inventory_ids:
            return operations_by_medication

        # Buscar todas las operaciones relacionadas con los inventarios del residente
        # Ordenadas por fecha descendente
        operations = self.env["operation.inventory"].search(
            [("medication_inventory_id", "in", inventory_ids)], order="date desc"
        )

        # Procesar cada operación
        for operation in operations:
            medicament_id = operation.medication_id.id

            # Si es la primera vez que encontramos este medicamento
            if medicament_id not in operations_by_medication:
                operations_by_medication[medicament_id] = {
                    "name_medicament": operation.medication_id.name or "",
                    "operations": [],
                }

            # Preparar los datos de la operación
            operation_data = {
                "date": self._convert_timezone(self.env.user, operation.date),
                "quantity": operation.quantity,
                "quantity_str": operation.quantity_str or "",
                "uom_id": operation.uom_id.name or "",
                "reason": operation.reason or "",
                "operation_type": operation.operation_type,
                "operation_type_label": dict(
                    operation._fields["operation_type"].selection
                ).get(operation.operation_type, ""),
                "user_id": operation.user_id.name or "",
                "family_id": operation.family_id.name if operation.family_id else "",
                "pharmaceutical_form": operation.pharmaceutical_form or "",
                "residence_id": operation.residence_id.name
                if operation.residence_id
                else "",
                "operation_id": operation.id,
            }

            # Agregar la operación a la lista del medicamento correspondiente
            operations_by_medication[medicament_id]["operations"].append(operation_data)

        values = list(operations_by_medication.values())

        return values

    def get_water_balance_summary(self):
        annotations = self.water_balance_ids.sorted(key=lambda r: r.date or "")

        # Agrupar por día
        by_day = defaultdict(list)
        for a in annotations:
            dt = a.date or a.write_date or a.create_date  # fallback
            day = dt.date() if dt else None
            by_day[day].append(a)

        # Totales por vía
        income_by_route = defaultdict(float)
        expense_by_route = defaultdict(float)
        for a in annotations:
            route_name = a.route_id.name or "Sin vía"
            if a.type_annotation == "income":
                income_by_route[route_name] += a.quantity
            else:
                expense_by_route[route_name] += a.quantity

        # Cálculos por día
        days = []
        for day, items in sorted(
            by_day.items(), key=lambda x: x[0] or datetime.min.date()
        ):
            income = sum(i.quantity for i in items if i.type_annotation == "income")
            expense = sum(i.quantity for i in items if i.type_annotation == "expense")
            diff = income - expense
            if income == 0 and expense == 0:
                status = "Sin registros"
            elif diff > 0:
                status = "Positivo"
            elif diff < 0:
                status = "Negativo"
            else:
                status = "Neutro"
            days.append(
                {
                    "date": day.strftime("%d/%m/%Y"),
                    "income": income,
                    "expense": expense,
                    "difference": diff,
                    "status": status,
                    "items": items,
                }
            )

        return [by_day, income_by_route, expense_by_route, days]

    def action_full_report_pdf(self):
        self.ensure_one()
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        date_server = datetime.now()
        date_user = self._convert_timezone(self.env.user, date_server)
        return (
            self.env.ref("sc_reports.report_resident_full_pdf")
            .with_context(website_url=base_url, date_user=date_user)
            .report_action(self, config=False)
        )

    def action_export_care_plan_pdf(self):
        self.ensure_one()
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        date_server = datetime.now()
        date_user = self._convert_timezone(self.env.user, date_server)
        return (
            self.env.ref("sc_reports.report_resident_plan_care_pdf")
            .with_context(website_url=base_url, date_user=date_user)
            .report_action(self, config=False)
        )

    def action_activity_recreation_report_pdf(self):
        self.ensure_one()
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        date_server = datetime.now()
        date_user = self._convert_timezone(self.env.user, date_server)
        date_limit = self._convert_timezone_datetime(
            self.env.user, date_server
        ) + timedelta(days=7)
        return (
            self.env.ref("sc_reports.report_resident_recreational_activity_pdf")
            .with_context(
                website_url=base_url, date_user=date_user, date_limit=date_limit
            )
            .report_action(self, config=False)
        )

    def action_medication_inventory_pdf(self):
        self.ensure_one()
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        date_server = datetime.now()
        date_user = self._convert_timezone(self.env.user, date_server)
        operations_inventory = self.get_medication_operations_summary()
        return (
            self.env.ref("sc_reports.report_resident_medication_inventory_pdf")
            .with_context(
                website_url=base_url,
                date_user=date_user,
                operations_inventory=operations_inventory,
            )
            .report_action(self, config=False)
        )

    def action_download_water_balance_pdf(self):
        self.ensure_one()
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        date_server = datetime.now()
        date_user = self._convert_timezone(self.env.user, date_server)
        [by_day, income_by_route, expense_by_route, days] = (
            self.get_water_balance_summary()
        )
        return (
            self.env.ref("sc_reports.report_resident_water_balance_pdf")
            .with_context(
                website_url=base_url,
                date_user=date_user,
                income_by_route=income_by_route,
                expense_by_route=expense_by_route,
                days=days,
            )
            .report_action(self, config=False)
        )

    def action_nutrition_report_pdf(self):
        self.ensure_one()
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        date_server = datetime.now()
        date_user = self._convert_timezone(self.env.user, date_server)
        date_limit = self._convert_timezone_datetime(
            self.env.user, date_server
        ) + timedelta(days=7)
        return (
            self.env.ref("sc_reports.report_resident_nutrition_pdf")
            .with_context(
                website_url=base_url, date_user=date_user, date_limit=date_limit
            )
            .report_action(self, config=False)
        )

    def action_hygiene_report_pdf(self):
        self.ensure_one()
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        date_server = datetime.now()
        date_user = self._convert_timezone(self.env.user, date_server)
        date_limit = self._convert_timezone_datetime(
            self.env.user, date_server
        ) + timedelta(days=7)
        return (
            self.env.ref("sc_reports.report_resident_hygiene_pdf")
            .with_context(
                website_url=base_url, date_user=date_user, date_limit=date_limit
            )
            .report_action(self, config=False)
        )

    def action_geriatric_neurological_assessment_report_pdf(self):
        self.ensure_one()
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        date_server = datetime.now()
        date_user = self._convert_timezone(self.env.user, date_server)
        return (
            self.env.ref(
                "sc_reports.report_resident_geriatric_neurological_assessment_pdf"
            )
            .with_context(
                website_url=base_url,
                date_user=date_user,
            )
            .report_action(self, config=False)
        )

    def action_family_report_pdf(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Informe a familiares",
            "res_model": "resident.family.report.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "active_id": self.id,
                "active_model": "resident",
            },
        }
