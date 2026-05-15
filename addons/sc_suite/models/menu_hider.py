import logging
import re
import os
import base64
from dateutil.relativedelta import relativedelta
from datetime import date

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied, UserError

_logger = logging.getLogger(__name__)

class MenuHider(models.Model):
    _name = 'menu.hider'
    _description = 'Utilidad para ocultar menús en Odoo 18'

    @api.model
    def hide_all_unwanted_menus(self):
        """Método final que combina todas las estrategias"""
        self._log("Iniciando ocultamiento de menús...")
        
        # Estrategia 1: XML IDs específicos
        specific_xml_ids = [
            'crm.crm_menu_root', 'note.menu_notes', 'calendar.menu_calendar_main',
            'contacts.menu_contacts', 'hr.menu_hr_root', 'hr.menu_hr_main', 'hr_attendance.menu_hr_attendance_root',
            'project.menu_main_pm', 'stock.menu_stock_root', 'project_todo.menu_todo_todos', 'utm.menu_link_tracker_root'
        ]
        
        for xml_id in specific_xml_ids:
            menu = self.env.ref(xml_id, raise_if_not_found=False)
            if menu:
                menu.active = False
                self._log(f"Ocultado por XML ID: {xml_id}")
        
        # Estrategia 2: Búsqueda por nombres clave
        keywords = ['CRM', 'Note', 'Calendar', 'Contact', 'HR', 'Attendance', 'Project', 'Inventory']
        for keyword in keywords:
            menus = self.env['ir.ui.menu'].search([('name', 'ilike', keyword)])
            for menu in menus:
                # Solo ocultar menús principales
                if not menu.parent_id or menu.parent_id.name in ['', 'Root']:
                    menu.active = False
                    self._log(f"Ocultado por nombre: {menu.name}")
        
        self._log("Proceso de ocultamiento completado")

    def _log(self, message):
        """Log para debugging"""
        _logger.info(f"MenuHider: {message}")

    def init(self):
        self.hide_all_unwanted_menus()