# -*- coding: utf-8 -*-
import logging
import re
from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ResidenceService(models.Model):
    _name = 'residence_service'
    _description = 'Servicio de la Residencia'
    _order = 'name'
    _rec_name = 'name'

    name = fields.Char(
        string='Nombre del Servicio',
        required=True,
        help='Nombre del servicio ofrecido'
    )
    description = fields.Text(
        string='Descripción',
        help='Descripción detallada del servicio'
    )
    active = fields.Boolean(
        string='Activo',
        default=True,
        help='Si está desmarcado, el servicio no aparecerá en las opciones'
    )
    slug = fields.Char(
        string="Slug", compute="_compute_slug", readonly=True, store=True
    )

    @api.depends("name")
    def _compute_slug(self):
        for record in self:
            record.slug = self._generate_slug(record.name)

    def _generate_slug(self, name):
        cleaned = re.sub(r"[^\w\-]+", "", str(name))
        slug = cleaned.replace(" ", "-")
        return slug.lower()

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, f"{record.name}"))
        return result

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            existing_record_slug = self.search(
                [
                    ("slug", "=", self._generate_slug(vals.get("name"))),
                ],
                limit=1,
            )

            if existing_record_slug:
                raise ValidationError(
                    f"Ya existe un servicio con el nombre '{vals['name']}'."
                )

        return super(ResidenceService, self).create(vals_list)

    def write(self, vals):
        if "name" in vals or "country_id" in vals:
            existing_record_slug = self.search(
                [
                    ("slug", "=", self._generate_slug(vals.get("name"))),
                    ("id", "!=", self.id),
                ],
                limit=1,
            )

            if existing_record_slug:
                raise ValidationError(
                    f"Ya existe un servicio con el nombre '{vals['name']}'."
                )

        return super(ResidenceService, self).write(vals)
