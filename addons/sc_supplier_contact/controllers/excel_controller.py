from odoo import http
import json
import xlsxwriter
import io
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class SupplierExcelReportController(http.Controller):
    @http.route(
        ["/supplier/excel_report/<string:record_ids>"],
        type="http",
        auth="user",
        csrf=False,
    )
    def get_supplier_excel_report(self, record_ids=None, **kwargs):
        try:
            # Convertir string de IDs a lista
            record_ids = json.loads(record_ids)

            # Obtener los registros
            supplier_model = request.env["supplier.base"]
            suppliers = supplier_model.browse(record_ids)

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
            worksheet = workbook.add_worksheet("Proveedores")

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
            headers = ["Nombre", "Tipo", "Teléfono", "Dirección"]
            for col, header in enumerate(headers):
                worksheet.write(0, col, header, header_format)
                worksheet.set_column(col, col, 25)  # Ancho de columna

            # Escribir datos
            for row, supplier in enumerate(suppliers, start=1):
                # Obtener etiqueta del campo de selección
                type_label = dict(supplier._fields["provider_type"].selection).get(
                    supplier.provider_type, ""
                )

                worksheet.write(row, 0, supplier.name or "", cell_format)
                worksheet.write(row, 1, type_label, cell_format)
                worksheet.write(row, 2, supplier.phone or "", cell_format)
                worksheet.write(row, 3, supplier.contact_address or "", cell_format)

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
