from odoo import http
import json
import xlsxwriter
import io
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class RecreationalActivityExcelReportController(http.Controller):
    @http.route(
        ["/recreational_activity/excel_report/<string:record_ids>"],
        type="http",
        auth="user",
        csrf=False,
    )
    def get_recreational_activity_excel_report(self, record_ids=None, **kwargs):
        try:
            # Convertir string de IDs a lista
            record_ids = json.loads(record_ids)

            # Obtener los registros
            recreational_activity_model = request.env["recreational.activity"]
            recreational_activity = recreational_activity_model.browse(record_ids)

            # Crear respuesta Excel
            response = request.make_response(
                None,
                headers=[
                    ("Content-Type", "application/vnd.ms-excel"),
                    (
                        "Content-Disposition",
                        'attachment; filename="Reporte_Proveedores.xlsx"',
                    ),
                ],
            )

            # Crear libro Excel en memoria
            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output, {"in_memory": True})
            worksheet = workbook.add_worksheet("Actividades Recreativas")

            # Definir formatos
            header_format = workbook.add_format(
                {
                    "bold": True,
                    "bg_color": "#5D9BD5",
                    "font_color": "white",
                    "align": "center",
                    "valign": "vcenter",
                    "border": 1,
                }
            )

            cell_format = workbook.add_format(
                {"align": "left", "valign": "vcenter", "border": 1}
            )

            # Escribir encabezados
            headers = ["Fecha/Hora", "Tipo de Actividad", "Registrada", "Residentes", "Descripción"]
            for col, header in enumerate(headers):
                worksheet.write(0, col, header, header_format)
                worksheet.set_column(col, col, 25)  # Ancho de columna

            # Escribir datos
            for row, activity in enumerate(recreational_activity, start=1):
                worksheet.write(row, 0, activity._convert_to_iso(activity.date_execution) or "", cell_format)
                worksheet.write(row, 1, activity.activity_type_id.name, cell_format)
                worksheet.write(row, 2, activity.user_id.name or "", cell_format)
                worksheet.write(row, 3, activity.residents_str or "", cell_format)
                worksheet.write(row, 4, activity.description or "", cell_format)

            workbook.close()
            output.seek(0)
            response.stream.write(output.read())
            output.close()

            return response

        except Exception as e:
            _logger.error("Error generating Excel report: %s", str(e))
            return request.make_response(
                "Error generando reporte Excel",
                headers=[("Content-Type", "text/plain")],
            )

    @http.route(
        ["/recreational_activity/excel_report_resident/<string:record_ids>"],
        type="http",
        auth="user",
        csrf=False,
    )
    def get_recreational_activity_excel_report_resident(self, record_ids=None, **kwargs):
        try:
            # Convertir string de IDs a lista
            record_ids = json.loads(record_ids)

            # Obtener los registros
            recreational_activity_model = request.env["resident.recreation.activity.rel"]
            recreational_activity = recreational_activity_model.browse(record_ids)

            # Crear respuesta Excel
            response = request.make_response(
                None,
                headers=[
                    ("Content-Type", "application/vnd.ms-excel"),
                    (
                        "Content-Disposition",
                        'attachment; filename="Reporte_Actividades_Recreativas_Residente.xlsx"',
                    ),
                ],
            )

            # Crear libro Excel en memoria
            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output, {"in_memory": True})
            worksheet = workbook.add_worksheet("Actividades Recreativas")

            # Definir formatos
            header_format = workbook.add_format(
                {
                    "bold": True,
                    "bg_color": "#5D9BD5",
                    "font_color": "white",
                    "align": "center",
                    "valign": "vcenter",
                    "border": 1,
                }
            )

            cell_format = workbook.add_format(
                {"align": "left", "valign": "vcenter", "border": 1}
            )

            # Escribir encabezados
            headers = ["Fecha/Hora", "Tipo de Actividad", "Registrada", "Residente", "Descripción"]
            for col, header in enumerate(headers):
                worksheet.write(0, col, header, header_format)
                worksheet.set_column(col, col, 25)  # Ancho de columna

            # Escribir datos
            for row, activity in enumerate(recreational_activity, start=1):
                worksheet.write(row, 0, activity.activity_id._convert_to_iso(activity.date_execution) or "", cell_format)
                worksheet.write(row, 1, activity.activity_type_id.name, cell_format)
                worksheet.write(row, 2, activity.user_id.name or "", cell_format)
                worksheet.write(row, 3, activity.resident_id.name or "", cell_format)
                worksheet.write(row, 4, activity.description or "", cell_format)

            workbook.close()
            output.seek(0)
            response.stream.write(output.read())
            output.close()

            return response

        except Exception as e:
            _logger.error("Error generating Excel report: %s", str(e))
            return request.make_response(
                "Error generando reporte Excel",
                headers=[("Content-Type", "text/plain")],
            )
