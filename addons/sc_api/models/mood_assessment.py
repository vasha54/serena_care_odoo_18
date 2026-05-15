from odoo import models, fields, api


class MoodAssessment(models.Model):
    _inherit = "mood.assessment"

    user = fields.Json(
        string="Usuario Datos",
        compute="_compute_user_data",
        store=False,
    )
    resident = fields.Json(
        string="Residente Datos",
        compute="_compute_resident_data",
        store=False,
    )
    mood_state = fields.Json(
        string="Estados Datos",
        compute="_compute_mood_state_data",
        store=False,
    )

    def _compute_mood_state_data(self):
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")

        for record in self:
            if record.mood_state_id:
                mood_data = record.mood_state_id.read(
                    [
                        "id",
                        "name",
                        "order",
                        "image",
                    ]
                )[0]

                if mood_data.get("image"):
                    mood_data["image"] = True
                    mood_data[
                        "image_url"
                    ] = f"{base_url}/public/image/mood_state/{mood_data['id']}"
                else:
                    mood_data["image"] = False
                    mood_data["image_url"] = None

                record.mood_state = mood_data
            else:
                record.mood_state = None

    def _compute_user_data(self):
        for record in self:
            record.user = record.user_id.read(
                [
                    "id",
                    "name",
                ]
            )[0]

    def _compute_resident_data(self):
        for record in self:
            record.resident = record.resident_id.read(
                [
                    "id",
                    "name",
                ]
            )[0]
