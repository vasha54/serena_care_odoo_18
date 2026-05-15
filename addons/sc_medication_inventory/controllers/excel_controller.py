
import json
import xlsxwriter
import io
from odoo.http import request
from odoo import _, fields, http
import logging

_logger = logging.getLogger(__name__)


class OperationInventoryExcelReportController(http.Controller):

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

    @http.route(
        ["/operation_inventory/excel_report/<string:record_ids>"],
        type="http",
        auth="user",
        csrf=False,
    )
    def get_supplier_excel_report(self, record_ids=None, **kwargs):
        try:
            # Convertir string de IDs a lista
            record_ids = json.loads(record_ids)

            # Obtener los registros
            model = request.env["operation.inventory"]
            records = model.browse(record_ids)

            # Crear respuesta Excel
            response = request.make_response(
                None,
                headers=[
                    ("Content-Type", "application/vnd.ms-excel"),
                    (
                        "Content-Disposition",
                        'attachment; filename="Reporte_Operaciones_Inventario.xlsx"',
                    ),
                ],
            )

            # Crear libro Excel en memoria
            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output, {"in_memory": True})
            worksheet = workbook.add_worksheet("Operaciones Inventario")

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
            headers = ["Fecha/Hora", "Tipo", "Registrado", "Medicamento", "Cantidad","Residente", "Residencia"]
            for col, header in enumerate(headers):
                worksheet.write(0, col, header, header_format)
                worksheet.set_column(col, col, 25)  # Ancho de columna

            # Escribir datos
            for row, record in enumerate(records, start=1):
                # Obtener etiqueta del campo de selección
                type_label = dict(record._fields["operation_type"].selection).get(
                    record.operation_type, ""
                )

                worksheet.write(row, 0, self._convert_to_iso(record.create_date) or "", cell_format)
                worksheet.write(row, 1, type_label, cell_format)
                worksheet.write(row, 2, record.user_id.name or "", cell_format)
                worksheet.write(row, 3, record.medication_id.name or "", cell_format)
                worksheet.write(row, 4, record.quantity_str or "", cell_format)
                worksheet.write(row, 5, record.resident_id.name or "", cell_format)
                worksheet.write(row, 6, record.residence_id.name or "", cell_format)

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
