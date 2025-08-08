# -*- coding: utf-8 -*-

from email import message
import logging
import datetime
from os import unlink
import re
from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


# Lista actualizada de LADAs válidas (2 y 3 dígitos)
VALID_LADAS = {
    '55', '81', '33', '656', '618', '744', '222', '246', '271', '272', '312', '315',
    '321', '330', '341', '342', '348', '351', '369', '443', '444', '449', '461', '462',
    '477', '479', '483', '484', '487', '494', '495', '498', '499', '614', '624', '627',
    '629', '631', '633', '634', '635', '636', '637', '638', '639', '641', '642', '643',
    '644', '645', '646', '647', '648', '649', '653', '658', '664', '665', '667', '668',
    '669', '671', '673', '674', '675', '676', '677', '678', '686', '687', '688', '689',
    '691', '692', '693', '694', '695', '696', '697', '771', '773', '774', '775', '776',
    '777', '779', '782', '783', '785', '786', '787', '788', '789', '831', '832', '833',
    '834', '835', '836', '837', '838', '841', '842', '843', '844', '845', '846', '847',
    '848', '867', '868', '869', '871', '872', '873', '874', '875', '876', '877', '878',
    '879', '894', '895', '896', '897', '899', '911', '912', '913', '914', '915', '916',
    '917', '918', '919', '921', '922', '923', '924', '925', '926', '927', '928', '929',
    '931', '932', '933', '934', '935', '936', '937', '938', '939', '941', '942', '943',
    '944', '945', '946', '947', '948', '949', '951', '961', '962', '963', '964', '965',
    '966', '967', '968', '969', '971', '972', '973', '974', '975', '976', '977', '978',
    '979', '981', '982', '983', '984', '985', '986', '987', '988', '989', '991', '992',
    '993', '994', '995', '996', '997', '998', '999'
}

class ResidenceHouse(models.Model):
    _name = 'residence_house'
    _description = 'Casas de Residencia'
    _order = 'name'
    _inherit = ['soft.delete.mixin']
    _inherits = {'res.partner':'partner_id'}
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Contacto',
        required=True,
        ondelete='cascade',     
    )
    
    description = fields.Html(string="Descripción")
    schedule = fields.Char(string='Horario de Atención', size=255)
    services_ids = fields.Many2many("residence_service", string="Servicios")
    

    @api.constrains('email')
    def _check_valid_email(self):
        for record in self:
            if record.email and '@' not in record.email:
                raise models.ValidationError("Formato de correo inválido (ejemplo@dominio.com)")

    @api.constrains('phone')
    def _check_phone_format(self):
        """Valida que el teléfono tenga formato mexicano válido (10 dígitos, con o sin +52)"""
        for record in self:
            if record.phone:
                # Eliminar TODOS los caracteres no numéricos (incluye +, espacios, guiones, etc.)
                clean_phone = re.sub(r'\D', '', record.phone)
            
                # Verificar si es número con código de país (12 dígitos incluyendo +52)
                if len(clean_phone) == 12 and clean_phone.startswith('52'):
                    clean_phone = clean_phone[2:]  # Remover código de país (52)
            
                # Validar longitud (10 dígitos después de limpiar)
                if len(clean_phone) != 10 or not clean_phone.isdigit():
                    raise ValidationError(
                        "Formato de teléfono inválido. Debe ser de 10 dígitos o incluir código de país (+52). "
                        "Ejemplos: 5512345678, 55 1234 5678, +525512345678"
                    )
            
                # Validar prefijo (LADA) en los primeros 2 o 3 dígitos
                # lada_2 = clean_phone[:2]
                # lada_3 = clean_phone[:3]
                # if lada_2 not in VALID_LADAS and lada_3 not in VALID_LADAS:
                #     raise ValidationError(
                #         "LADA no válida. Prefijos aceptados: "
                #         "55 (CDMX), 81 (Monterrey), 33 (Guadalajara), 656 (Cd. Juárez), etc."
                #     )

    
    def unlink(self):
        residents = 0
        employees = 0
        
        if 'resident_count' in self.env['residence_house'].fields_get():
            residents = self.resident_count
        else:
            _logger.warning("No find field 'resident_count' in model 'residence_house'")

        if 'employee_count' in self.env['residence_house'].fields_get():
            employees = self.employee_count
        else:
            _logger.warning("No find field 'resident_count' in model 'residence_house'")

        if residents > 0 or employees > 0:
           message = f"No se puede eliminar la residencia {self.name}. "
           message +=  f"Reubique primero los residentes ({residents}) y empleados ({employees}) de la residencia."
           raise ValidationError(message)

        return self.action_soft_delete()