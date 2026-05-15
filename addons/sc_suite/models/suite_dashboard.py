import logging
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied
from odoo.tools import format_date

from datetime import datetime, timedelta
from pytz import timezone
from babel.dates import format_date as babel_format_date

_logger = logging.getLogger(__name__)


class SuiteDashboard(models.Model):
    _name = "suite.dashboard"
    _description = "Suite Dashboard"

    @api.model
    def get_filter_residence(self):
        # Ejecutar como superusuario para evitar reglas de registro
        user = self.env.user.sudo()
        
        selected_residences = user.selected_residences_ids.sudo()
        accessible_residences = user.accessible_residences_ids.sudo()

        accessible_list = [
            {"id": r.id, "name": r.name}
            for r in accessible_residences
        ]
        selected_list = [
            {"id": r.id, "name": r.name}
            for r in selected_residences
        ]

        return {
            "user_id": user.id,
            "selected_count": len(selected_residences),
            "selected_ids": selected_residences.ids,
            "accessible_count": len(accessible_residences),
            "accessible_ids": accessible_residences.ids,
            "accessible": accessible_list,
            "selected": selected_list,
        }


    @api.model
    def get_count_residents(self):
        user = self.env.user

        selected_residences = user.selected_residences_ids
        count_residents = 0
        residence_ids = selected_residences.mapped("id")
        count_residents = (
            self.env["resident"]
            .sudo()
            .search_count(
                domain=[
                    ("residence_id", "in", residence_ids),
                    ("active", "=", True),
                    ("is_deleted", "=", False),
                ]
            )
        )
        return {"count_residents": count_residents}

    @api.model
    def get_age_average(self):
        user = self.env.user
        selected_residences = user.selected_residences_ids
        residence_ids = selected_residences.mapped("id")

        residents = (
            self.env["resident"]
            .sudo()
            .search(
                domain=[
                    ("residence_id", "in", residence_ids),
                    ("active", "=", True),
                    ("is_deleted", "=", False),
                ]
            )
        )

        # Manejar el caso cuando no hay residentes
        if not residents:
            return {"age_average": 0.0}

        # Calcular el promedio redondeado a un decimal
        ages = [record.age for record in residents if record.age]
        if not ages:  # Si no hay edades válidas
            return {"age_average": 0.0}

        age_average = round(sum(ages) / len(ages), 1)

        return {"age_average": age_average}

    @api.model
    def get_sex_distribution(self):
        user = self.env.user

        selected_residences = user.selected_residences_ids
        residence_ids = selected_residences.mapped("id")

        male = self.env.ref("sc_sex.gender_male", raise_if_not_found=False)
        female = self.env.ref("sc_sex.gender_female", raise_if_not_found=False)
        residents_male = (
            self.env["resident"]
            .sudo()
            .search_count(
                domain=[
                    ("residence_id", "in", residence_ids),
                    ("active", "=", True),
                    ("is_deleted", "=", False),
                    ("sex_id", "=", male.id),
                ]
            )
            if male
            else 0
        )
        residents_female = (
            self.env["resident"]
            .sudo()
            .search_count(
                domain=[
                    ("residence_id", "in", residence_ids),
                    ("active", "=", True),
                    ("is_deleted", "=", False),
                    ("sex_id", "=", female.id),
                ]
            )
            if female
            else 0
        )

        return {
            "residents_male": residents_male,
            "residents_female": residents_female,
        }

    @api.model
    def get_health_status(self):
        try:
            user = self.env.user
            selected_residences = user.selected_residences_ids

            # Si no hay residencias seleccionadas, devolver estructura vacía
            if not selected_residences:
                return self._get_empty_age_distribution()

            residence_ids = selected_residences.mapped("id")

            residents = (
                self.env["resident"]
                .sudo()
                .search(
                    domain=[
                        ("residence_id", "in", residence_ids),
                        ("active", "=", True),
                        ("is_deleted", "=", False),
                    ]
                )
            )
            colors = [
                "#95a5a6",  # Gris - Desconocido
                "#e74c3c",  # Rojo - Crítico
                "#f39c12",  # Naranja - En Observación
                "#27ae60",  # Verde - Estable
            ]
            texts = ["Desconocido", "Crítico", "En Observación", "Estable"]
            status_ranges = [0, 0, 0, 0]  # Uno por cada estado

            MedicalState = self.env["medical.resident.state"].sudo()

            last_states = MedicalState.search(
                [("resident_id", "in", residents.ids)], order="resident_id, date desc"
            )

            seen_residents = set()

            for state in last_states:
                if state.resident_id.id in seen_residents:
                    continue

                seen_residents.add(state.resident_id.id)

                status = state.general_status_int
                if status == -1:
                    status_ranges[0] += 1
                elif status == 0:
                    status_ranges[1] += 1
                elif status == 1:
                    status_ranges[2] += 1
                elif status == 2:
                    status_ranges[3] += 1
                else:
                    status_ranges[0] += 1

            # Los residentes sin ningún estado → Desconocido
            status_ranges[0] += len(residents) - len(seen_residents)

            total_residents = sum(status_ranges)

            # Calcular porcentajes
            if total_residents > 0:
                percentages = [
                    round((count / total_residents) * 100, 2) for count in status_ranges
                ]
            else:
                percentages = [0, 0, 0, 0, 0, 0]
            answer = {
                "total": total_residents,
                "colors": colors,
                "texts": texts,
                "values": status_ranges,
                "values_percent": percentages,
                "has_data": total_residents > 0,
            }
            _logger.debug(f"Answer in get_distribution_age: {answer}")
            return answer

        except Exception as e:
            _logger.error(f"Error in get_health_status: {str(e)}")
            return self._get_empty_get_health_status()

    @api.model
    def get_distribution_age(self):
        try:
            user = self.env.user
            selected_residences = user.selected_residences_ids

            # Si no hay residencias seleccionadas, devolver estructura vacía
            if not selected_residences:
                return self._get_empty_age_distribution()

            residence_ids = selected_residences.mapped("id")

            residents = (
                self.env["resident"]
                .sudo()
                .search(
                    domain=[
                        ("residence_id", "in", residence_ids),
                        ("active", "=", True),
                        ("is_deleted", "=", False),
                    ]
                )
            )

            # Inicializar contadores
            colors = ["#4E79A7", "#F28E2B", "#E15759", "#76B7B2", "#59A14F", "#EDC948"]
            age_ranges = [0, 0, 0, 0, 0, 0]  # Uno por cada rango
            age_labels = [
                (0, 59),  # Menos de 60
                (60, 69),  # 60-69
                (70, 79),  # 70-79
                (80, 89),  # 80-89
                (90, 99),  # 90-99
                (100, 999),  # 100 o más (asumiendo edad máxima razonable)
            ]
            texts = [
                "Menos de 60 años",
                "60 - 69 años",
                "70 - 79 años",
                "80 - 89 años",
                "90 - 99 años",
                "Más de 100 años",
            ]

            # Clasificar residentes
            for resident in residents:
                if not resident.age:
                    continue

                age = resident.age
                for i, (min_age, max_age) in enumerate(age_labels):
                    if min_age <= age <= max_age:
                        age_ranges[i] += 1
                        break

            total_residents = sum(age_ranges)

            # Calcular porcentajes
            if total_residents > 0:
                percentages = [
                    round((count / total_residents) * 100, 2) for count in age_ranges
                ]
            else:
                percentages = [0, 0, 0, 0, 0, 0]

            legends = []

            for i in range(0, len(age_ranges)):
                legends.append(
                    {
                        "label": texts[i],
                        "value": age_ranges[i],
                        "percent": percentages[i],
                        "color": colors[i],
                    }
                )

            # Construir respuesta
            answer = {
                "total": total_residents,
                "colors": colors,
                "texts": texts,
                "values": age_ranges,
                "values_percent": percentages,
                "legends": legends,
                "has_data": total_residents > 0,
            }
            _logger.debug(f"Answer in get_distribution_age: {answer}")
            return answer

        except Exception as e:
            _logger.error(f"Error in get_distribution_age: {str(e)}")
            return self._get_empty_age_distribution()

    def _get_empty_get_health_status(self):
        """Devuelve una estructura de estado de salud vacia vacía"""
        colors = [
            "#95a5a6",  # Gris - Desconocido
            "#e74c3c",  # Rojo - Crítico
            "#f39c12",  # Naranja - En Observación
            "#27ae60",  # Verde - Estable
        ]
        texts = ["Desconocido", "Crítico", "En Observación", "Estable"]
        status_ranges = [0, 0, 0, 0]  # Uno por cada estado
        percentages = [25, 25, 25, 25]

        return {
            "total": 0,
            "colors": colors,
            "texts": texts,
            "values": status_ranges,
            "values_percent": percentages,
            "has_data": False,
        }

    def _get_empty_age_distribution(self):
        """Devuelve una estructura de distribución de edad vacía"""
        legends = []
        colors = ["#4E79A7", "#F28E2B", "#E15759", "#76B7B2", "#59A14F", "#EDC948"]
        texts = [
            "Menos de 60 años",
            "60 - 69 años",
            "70 - 79 años",
            "80 - 89 años",
            "90 - 99 años",
            "Más de 100 años",
        ]
        age_ranges = [0, 0, 0, 0, 0, 0]  # Uno por cada rango
        percentages = [16.7, 16.7, 16.7, 16.7, 16.7, 16.7]

        for i in range(0, len(age_ranges)):
            legends.append(
                {
                    "label": texts[i],
                    "value": age_ranges[i],
                    "percent": percentages[i],
                    "color": colors[i],
                }
            )

        return {
            "total": 0,
            "colors": colors,
            "texts": texts,
            "values": age_ranges,
            "values_percent": percentages,
            "legends": legends,
            "has_data": False,
        }

    @api.model
    def get_time_average_residence(self):
        """
        Calcula el promedio de tiempo de residencia y retorna en unidad apropiada
        Versión mejorada con validaciones adicionales
        """
        try:
            user = self.env.user
            if not user.selected_residences_ids:
                return {
                    "value": 0.0,
                    "unit": "días",
                    "message": "No hay residencias seleccionadas",
                }

            selected_residences = user.selected_residences_ids
            residence_ids = selected_residences.mapped("id")
            residents = (
                self.env["resident"]
                .sudo()
                .search(
                    domain=[
                        ("residence_id", "in", residence_ids),
                        ("active", "=", True),
                        ("is_deleted", "=", False),
                    ]
                )
            )

            if not residents:
                return {
                    "value": 0.0,
                    "unit": "días",
                    "message": "No hay residentes activos",
                }

            total_days = 0
            resident_count = 0
            for resident in residents:
                days = resident.get_days_since_registration()
                total_days += days
                resident_count += 1

            avg_days = total_days / resident_count

            result = self._convert_days_to_appropriate_unit(avg_days)
            result.update(
                {
                    "total_residents": resident_count,
                    "total_days": total_days,
                    "avg_days_raw": round(avg_days, 2),
                }
            )

            return result

        except Exception as e:
            return {"value": 0.0, "unit": "días", "error": str(e)}

    def _convert_days_to_appropriate_unit(self, days):
        """
        Convierte días a la unidad más apropiada
        """
        if days < 1:
            # Menos de un día - mostrar en horas
            hours = round(days * 24, 1)
            return {"value": hours, "unit": "horas"}
        elif days < 30:
            # Menos de un mes - mostrar en días
            return {"value": round(days, 2), "unit": "días"}
        elif days < 365:
            # Menos de un año - mostrar en meses
            months = days / 30.44  # Promedio de días por mes
            return {"value": round(months, 2), "unit": "meses"}
        else:
            # Un año o más - mostrar en años
            years = days / 365.25  # Promedio de días por año
            return {"value": round(years, 2), "unit": "años"}

    @api.model
    def get_appointment_today(self):
        try:
            user = self.env.user
            selected_residences = user.selected_residences_ids

            # Si no hay residencias seleccionadas, devolver estructura vacía
            if not selected_residences:
                return self._get_empty_age_distribution()

            residence_ids = selected_residences.mapped("id")

            residents = (
                self.env["resident"]
                .sudo()
                .search(
                    domain=[
                        ("residence_id", "in", residence_ids),
                        ("active", "=", True),
                        ("is_deleted", "=", False),
                    ]
                )
            )
            resident_ids = residents.mapped("id")

            # Obtener la fecha actual en la zona horaria del usuario
            today_date_str = fields.Date.context_today(self)  # Formato: YYYY-MM-DD

            # Crear fechas de inicio y fin del día en la zona horaria del usuario
            start_of_day_user = f"{today_date_str} 00:00:00"
            end_of_day_user = f"{today_date_str} 23:59:59"

            # Convertir a UTC usando tu función _adjust_timezone
            start_of_day_utc = self._adjust_timezone(user, start_of_day_user)
            end_of_day_utc = self._adjust_timezone(user, end_of_day_user)

            # Buscar citas médicas para hoy de los residentes seleccionados
            appointments = (
                self.env["calendar.note"]
                .sudo()
                .search(
                    domain=[
                        ("resident_id", "in", resident_ids),
                        ("event_type", "=", "appointment_doctor"),
                        ("start_date", ">=", start_of_day_utc),
                        ("start_date", "<=", end_of_day_utc),
                    ],
                    order="start_date asc",  # Ordenar por fecha ascendente
                )
            )
            base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
            # Formatear los datos de las citas
            appointment_list = []
            for appointment in appointments:
                resident = appointment.resident_id
                has_avatar = False
                url_avatar = False
                if resident and resident.image_1920:
                    has_avatar = True
                    url_avatar = (
                        f"{base_url}/public/image/resident/{appointment.resident_id.id}"
                    )
                appointment_list.append(
                    {
                        "id": appointment.id,
                        "resident_name": appointment.resident_id.name or "",
                        "resident_id": appointment.resident_id.id,
                        "doctor_name": appointment.doctor_id.name
                        if appointment.doctor_id
                        else "",
                        "doctor_id": appointment.doctor_id.id
                        if appointment.doctor_id
                        else False,
                        "specialty": appointment.specialty_doctor.name
                        if appointment.specialty_doctor
                        else "",
                        "specialty_id": appointment.specialty_doctor.id
                        if appointment.specialty_doctor
                        else False,
                        "start_date": appointment.start_date,
                        "time": self._format_date_for_user(
                            user, appointment.start_date
                        ),
                        "has_avatar": has_avatar,
                        "url_avatar": url_avatar,
                    }
                )

            return {
                "has_data": len(appointment_list) > 0,
                "appointments": appointment_list,
            }
        except Exception as e:
            return self._get_empty_appointment_today()

    def _get_empty_appointment_today(self):
        return {"has_data": False, "appointments": []}

    def _adjust_timezone(self, _user, _date):
        """Convierte fecha/hora de la zona del usuario a UTC"""
        _logger.info(f"User tz: {_user.tz}")
        user_tz = timezone(_user.tz or "UTC")
        utc_tz = timezone("UTC")
        # Convertir de la zona del usuario a UTC
        local_dt = user_tz.localize(datetime.strptime(_date, "%Y-%m-%d %H:%M:%S"))
        utc_dt = local_dt.astimezone(utc_tz)
        return utc_dt.strftime("%Y-%m-%d %H:%M:%S")

    def _format_date_for_user(self, user, datetime_utc):
        """Formatea un datetime UTC a la zona horaria del usuario"""
        if not datetime_utc:
            return ""

        try:
            user_tz = timezone(user.tz or "UTC")
            utc_tz = timezone("UTC")

            # Convertir el string UTC a datetime objeto
            if isinstance(datetime_utc, str):
                dt_utc = datetime.strptime(datetime_utc, "%Y-%m-%d %H:%M:%S")
            else:
                dt_utc = datetime_utc

            # Localizar como UTC y convertir a zona del usuario
            utc_dt = utc_tz.localize(dt_utc)
            user_dt = utc_dt.astimezone(user_tz)

            # Formatear a string amigable
            return user_dt.strftime("%I:%M %p")
        except Exception as e:
            _logger.error(f"Error formatting date: {e}")
            return str(datetime_utc) if datetime_utc else ""

    @api.model
    def get_week_appointments(self):
        try:
            user = self.env.user
            selected_residences = user.selected_residences_ids

            # Si no hay residencias seleccionadas, devolver estructura vacía
            if not selected_residences:
                return self._get_empty_age_distribution()

            residence_ids = selected_residences.mapped("id")

            residents = (
                self.env["resident"]
                .sudo()
                .search(
                    domain=[
                        ("residence_id", "in", residence_ids),
                        ("active", "=", True),
                        ("is_deleted", "=", False),
                    ]
                )
            )
            resident_ids = residents.mapped("id")

            # Fecha actual en la zona horaria del usuario (date)
            today_date = fields.Date.context_today(self)

            # Inicio del día actual (usuario)
            start_of_day_user = f"{today_date} 00:00:00"

            # Fin del día 7 días después (usuario)
            end_date = today_date + timedelta(days=6)
            end_of_day_user = f"{end_date} 23:59:59"

            # Convertir a UTC usando tu función existente
            start_of_day_utc = self._adjust_timezone(user, start_of_day_user)
            end_of_day_utc = self._adjust_timezone(user, end_of_day_user)

            appointments = (
                self.env["calendar.note"]
                .sudo()
                .search(
                    [
                        ("resident_id", "in", resident_ids),
                        ("event_type", "=", "appointment_doctor"),
                        ("start_date", ">=", start_of_day_utc),
                        ("start_date", "<", end_of_day_utc),
                        ("doctor_id", "!=", False),
                    ]
                )
            )

            if not appointments:
                return self._get_empty_week_appointments()

            labels = ["Hoy"]
            labels += [
                babel_format_date(
                    today_date + timedelta(days=i),
                    format="EEE",
                    locale="es"
                ).capitalize()
                for i in range(1, 7)
            ]

            # Estructura: {specialty_id: [0,0,0,0,0,0,0]}
            specialty_map = {}

            for app in appointments:
                specialty = app.specialty_doctor
                if not specialty:
                    continue

                day_index = (app.start_date.date() - today_date).days
                if day_index < 0 or day_index > 6:
                    continue

                if specialty.id not in specialty_map:
                    specialty_map[specialty.id] = {
                        "label": specialty.name,
                        "data": [0] * 7,
                    }

                specialty_map[specialty.id]["data"][day_index] += 1

            color_palette = [
                "#1F77B4",  # azul
                "#FF7F0E",  # naranja
                "#2CA02C",  # verde
                "#D62728",  # rojo
                "#9467BD",  # morado
                "#8C564B",  # marrón
                "#E377C2",  # rosa
                "#BCBD22",  # oliva
                "#17BECF",  # cian
                "#AEC7E8",  # azul claro
                "#FFBB78",  # naranja claro
                "#98DF8A",  # verde claro
                "#FF9896",  # rojo claro
                "#C5B0D5",  # lila
                "#F7B6D2",  # rosa claro
                "#DBDB8D",  # amarillo claro
            ]

            datasets = []
            for idx, spec in enumerate(specialty_map.values()):
                datasets.append(
                    {
                        "label": spec["label"],
                        "data": spec["data"],
                        "backgroundColor": color_palette[idx % len(color_palette)],
                        "borderColor": color_palette[idx % len(color_palette)],
                        "borderWidth": 1,
                        "borderRadius": 10, # Bordes redondeados para todas las barras
                        "borderSkipped": False,
                    }
                )

            return {
                "has_data": True,
                "labels": labels,
                "dataset": datasets,
            }

        except Exception as e:
            return self._get_empty_week_appointments()

    def _get_empty_week_appointments(self):
        return {
            "has_data": False,
            "labels": [],
            "dataset": [],
        }

    @api.model
    def save_residence_selection(self, selected_ids):
        user = self.env.user.sudo()
        residences = self.env['residence_house'].sudo().browse(selected_ids)

        user._compute_accessible_residences()
        accessible_residences = user.accessible_residences_ids.sudo()
        valid_residences = residences.filtered(lambda r: r in accessible_residences)

        user.write({'selected_residences_ids': [(6, 0, residences.ids)]})

        # invalidar caches ORM
        self.env.invalidate_all()
        # invalidar cache del campo concreto (opcional)
        self.env['res.users']._invalidate_cache(['selected_residences_ids'], [user.id])
        
        # limpiar contexto de sesión (igual que cambio de compañía) 
        from odoo.http import request 
        if hasattr(request, "session"): 
            request.session.context = {}

        # notificar otras pestañas del mismo usuario para que recarguen
        try:
            self.env['bus.bus'].sendmany([((self._cr.dbname, 'res.users', user.id), {'type': 'reload'})])
        except Exception:
            # no crítico si falla el bus
            pass

        # forzar recarga del cliente que llamó
        return {"type": "ir.actions.client", "tag": "reload_context"}

