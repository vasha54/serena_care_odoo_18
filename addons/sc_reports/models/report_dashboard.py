from odoo import models, fields, api

class ReportDashboard(models.TransientModel):
    _name = 'report.dashboard'
    _description = 'Dashboard de Reportes Serena'
    
    name = fields.Char(default="Pizarra Operativa de Reportes")

    def _show_not_implemented(self, message):
        """Método helper para mostrar mensajes de no implementado"""
        return self.env['not.implemented.wizard'].action_show_warning(message)

    def action_open_hydric_balance(self):
        return self._show_not_implemented("El reporte de Balance Hídrico no está implementado")
    
    def action_open_feeding_report(self):
        return self._show_not_implemented("El reporte de Alimentación se encuentra en desarrollo")
    
    def action_open_hygiene_report(self):
        return self._show_not_implemented("El reporte de Higiene/Aseo no está implementado")
    
    def action_open_consciousness_report(self):
        return self._show_not_implemented("El reporte de Estados de Conciencia no está implementado")
    
    def action_open_neurological_report(self):
        return self._show_not_implemented("El reporte de Evaluaciones Neurológicas no está implementado")
    
    def action_open_recreation_report(self):
        return self._show_not_implemented("El reporte de Recreación no está implementado")
    
    def action_open_medication_report(self):
        return self._show_not_implemented("El reporte de Medicamentos no está implementado")
    
    def action_open_care_plan_report(self):
        return self._show_not_implemented("El reporte de Plan de Cuidados no está implementado")
    
    def action_open_general_resident_report(self):
        return self._show_not_implemented("El reporte General de Residentes estará disponible pronto")