# sc_reports/controllers/report_water_balance_xlsx.py
import io
import logging
from collections import defaultdict
from datetime import datetime
from odoo import http
from odoo.http import request
import xlsxwriter

_logger = logging.getLogger(__name__)

class WaterBalanceXlsxController(http.Controller):

    @http.route(['/sc_reports/water_balance_xlsx/<int:resident_id>'], type='http', auth='user')
    def download_water_balance_xlsx(self, resident_id, **kw):
        # Obtener residente y anotaciones
        resident = request.env['resident'].sudo().browse(resident_id)
        if not resident.exists():
            return request.not_found()

        annotations = resident.water_balance_ids.sudo().sorted(key=lambda r: r.create_date or '')

        # Agrupar por día
        by_day = defaultdict(list)
        for a in annotations:
            dt = (a.create_date or a.write_date or a.create_date)
            day = dt.date() if dt else None
            by_day[day].append(a)

        # Preparar datos por día
        days = []
        for day, items in sorted(by_day.items(), key=lambda x: x[0] or datetime.min.date()):
            income = sum(i.quantity for i in items if i.type_annotation == 'income')
            expense = sum(i.quantity for i in items if i.type_annotation == 'expense')
            diff = income - expense
            if income == 0 and expense == 0:
                status = 'Sin registros'
            elif diff > 0:
                status = 'Positivo'
            elif diff < 0:
                status = 'Negativo'
            else:
                status = 'Neutro'
            days.append({
                'date': day and day.strftime('%Y-%m-%d') or '',
                'income': income,
                'expense': expense,
                'difference': diff,
                'status': status,
            })

        # Totales por vía
        income_by_route = defaultdict(float)
        expense_by_route = defaultdict(float)
        for a in annotations:
            route_name = a.route_id.name or 'Sin vía'
            if a.type_annotation == 'income':
                income_by_route[route_name] += a.quantity
            else:
                expense_by_route[route_name] += a.quantity

        all_records = [{
            'date': (a.create_date and a.create_date.strftime('%Y-%m-%d %H:%M')) or '',
            'doctor': a.user_id.display_name or '',
            'type': dict(a._fields['type_annotation'].selection).get(a.type_annotation, ''),
            'route': a.route_id.name or '',
            'quantity': a.quantity,
            'notes': a.notes or '',
        } for a in annotations]

        total_income = sum(income_by_route.values())
        total_expense = sum(expense_by_route.values())
        total_difference = total_income - total_expense

        # Crear archivo XLSX en memoria
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        # Formatos
        bold = workbook.add_format({'bold': True})
        money_fmt = workbook.add_format({'num_format': '#,##0.00'})
        header_fmt = workbook.add_format({'bold': True, 'bg_color': '#F2F2F2', 'border':1})
        date_fmt = workbook.add_format({'num_format': 'yyyy-mm-dd'})

        # Hoja: Resumen por día
        ws = workbook.add_worksheet('Resumen por día')
        ws.set_column(0, 0, 18)
        ws.set_column(1, 4, 16)
        headers = ['Día', 'Ingresos (ml)', 'Egresos (ml)', 'Diferencia (ml)', 'Estado']
        for col, h in enumerate(headers):
            ws.write(0, col, h, header_fmt)
        for row_idx, d in enumerate(days, start=1):
            ws.write(row_idx, 0, d['date'])
            ws.write_number(row_idx, 1, d['income'], money_fmt)
            ws.write_number(row_idx, 2, d['expense'], money_fmt)
            ws.write_number(row_idx, 3, d['difference'], money_fmt)
            ws.write(row_idx, 4, d['status'])

        # Hoja: Ingresos por vía
        ws2 = workbook.add_worksheet('Ingresos por vía')
        ws2.set_column(0, 0, 40)
        ws2.set_column(1, 1, 18)
        ws2.write(0, 0, 'Vía', header_fmt)
        ws2.write(0, 1, 'Total (ml)', header_fmt)
        for row_idx, (route, value) in enumerate(sorted(income_by_route.items(), key=lambda x: x[0]), start=1):
            ws2.write(row_idx, 0, route)
            ws2.write_number(row_idx, 1, value, money_fmt)

        # Hoja: Egresos por vía
        ws3 = workbook.add_worksheet('Egresos por vía')
        ws3.set_column(0, 0, 40)
        ws3.set_column(1, 1, 18)
        ws3.write(0, 0, 'Vía', header_fmt)
        ws3.write(0, 1, 'Total (ml)', header_fmt)
        for row_idx, (route, value) in enumerate(sorted(expense_by_route.items(), key=lambda x: x[0]), start=1):
            ws3.write(row_idx, 0, route)
            ws3.write_number(row_idx, 1, value, money_fmt)

        # Hoja: Listado completo
        ws4 = workbook.add_worksheet('Listado registros')
        cols = ['Fecha', 'Doctor', 'Tipo', 'Vía', 'Cantidad (ml)', 'Observación']
        for col, h in enumerate(cols):
            ws4.write(0, col, h, header_fmt)
        ws4.set_column(0, 0, 20)
        ws4.set_column(1, 1, 25)
        ws4.set_column(2, 3, 18)
        ws4.set_column(4, 4, 16)
        ws4.set_column(5, 5, 40)
        for row_idx, r in enumerate(all_records, start=1):
            ws4.write(row_idx, 0, r['date'])
            ws4.write(row_idx, 1, r['doctor'])
            ws4.write(row_idx, 2, r['type'])
            ws4.write(row_idx, 3, r['route'])
            ws4.write_number(row_idx, 4, r['quantity'], money_fmt)
            ws4.write(row_idx, 5, r['notes'])

        # Hoja: Totales resumen
        ws5 = workbook.add_worksheet('Totales')
        ws5.set_column(0, 0, 40)
        ws5.set_column(1, 1, 20)
        ws5.write(0, 0, 'Concepto', header_fmt)
        ws5.write(0, 1, 'Valor', header_fmt)
        ws5.write(1, 0, 'Total ingresos (ml)')
        ws5.write_number(1, 1, total_income, money_fmt)
        ws5.write(2, 0, 'Total egresos (ml)')
        ws5.write_number(2, 1, total_expense, money_fmt)
        ws5.write(3, 0, 'Diferencia (ml)')
        ws5.write_number(3, 1, total_difference, money_fmt)

        # Metadata y cierre
        workbook.close()
        output.seek(0)
        filecontent = output.read()

        filename = f"{resident.name or 'Residente'} Balance Hídrico.xlsx"

        # Devolver como attachment
        return request.make_response(
            filecontent,
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', f'attachment; filename="{filename}"'),
            ],
        )
