# -*- coding: utf-8 -*-
from . import controllers
from . import models
from . import wizard 
from odoo import api

import logging
_logger = logging.getLogger(__name__)

def post_init_hook(env):
    _logger.info("Ejecutando post_init_hook sc_base")
    env['res.company'].sudo()._set_default_company()

def post_update_hook(env):
    _logger.info("Ejecutando post_update_hook sc_base")
    env['res.company'].sudo()._set_default_company()
