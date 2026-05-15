import yaml
import re
import logging
import json
from odoo import http
from odoo.http import Response, request

from .uom import controllers_category_uom as ccuom, controllers_oum as cuom
from .auth import controllers_auth
from .residence import controllers_residence
from .medical_indication import controllers_medical_indication
from .recreational_activity import (
    controllers_activity_type,
    controllers_recreational_activity,
)
from .medication_inventory import controllers_operation_inventory
from .vital_signs import controllers_vital_signs
from .water_balance import (
    controllers_water_balance_annotation,
    controllers_water_balance_route,
)
from .resident import controllers_resident
from .calendar import controllers_calendar_note
from .nursing_note import controllers_nursing_note
from .medical_note import controllers_medical_note
from .anomalies import controllers_anomaly, controllers_anomaly_level
from .nutrition import controllers_nutrition, controllers_nutrition_level
from .care_plan import controllers_care_plan
from .mood import (
    controller_mood_assessment,
    controller_mood_answer,
    controller_mood_state,
)
from .hygiene import (
    controllers_hygiene,
    controllers_hygiene_type,
    controllers_evacuation_type,
)
from .neurological_assessment import (
    controllers_neurological_state,
    controllers_neurological_assessment,
)
from .pain_scale import controllers_pain_scale
from .geriatric_assessment import controllers_norton_assessment
from .geriatric_assessment import (
    controllers_scalegds5_question,
    controllers_scalegds5_answer,
    controllers_scalegds5_assessment,
)
from .geriatric_assessment import (
    controllers_scalefrail_answer,
    controllers_scalefrail_question,
    controllers_scalefrail_assessment,
)
from .geriatric_assessment import (
    controllers_scalesarcf_question,
    controllers_scalesarcf_answer,
    controllers_scalesarcf_assessment,
)
from .geriatric_assessment import (
    controllers_barthel_assessment,
    controllers_barthel_answer,
    controllers_barthel_question,
)
from .geriatric_assessment import (
    controllers_lawton_brody_answer,
    controllers_lawton_brody_assessment,
    controllers_lawton_brody_question,
)
from .employee import controllers_user
from .general_condition_resident import controllers_medical_resident_state
from .laboratory_study import controllers_laboratory_study

_logger = logging.getLogger(__name__)


class APIDocsController(http.Controller):
    @http.route("/api-docs", type="http", auth="public", methods=["GET"])
    def get_api_docs(self, **kwargs):
        """
        Endpoint para documentación Swagger/OpenAPI
        ---
        tags:
          - Documentation
        summary: Obtener documentación de la API en formato OpenAPI
        description: Retorna la especificación OpenAPI de todos los endpoints disponibles
        responses:
          200:
            description: Documentación OpenAPI
            content:
              application/json:
                schema:
                  type: object
        """
        # Generar la especificación OpenAPI
        openapi_spec = self._generate_openapi_spec()

        # Si el cliente solicita JSON, retornar la especificación
        if request.httprequest.headers.get("Accept") == "application/json":
            return Response(
                json.dumps(openapi_spec), headers={"Content-Type": "application/json"}
            )

        # Retornar la interfaz HTML con Swagger UI
        return self._render_swagger_ui(openapi_spec)

    @http.route("/api-docs/json", type="http", auth="public", methods=["GET"])
    def get_api_docs_json(self, **kwargs):
        """
        Endpoint para obtener solo el JSON de la documentación OpenAPI
        """
        openapi_spec = self._generate_openapi_spec()
        return Response(
            json.dumps(openapi_spec), headers={"Content-Type": "application/json"}
        )

    def _generate_openapi_spec(self):
        """Genera la especificación OpenAPI completa"""
        auth_controller = controllers_auth.AuthAPIController()
        residence = controllers_residence.ResidenceAPIController()
        medical_indication = (
            controllers_medical_indication.MedicalIndicationController()
        )
        activity_recreational_type = (
            controllers_activity_type.ActivityRecreationalTypeAPIController()
        )
        recreational_activity = (
            controllers_recreational_activity.ActivityRecreationalAPIController()
        )
        cat_uom = ccuom.CategoryUoMController()
        uom = cuom.UoMController()
        operation_inventory = (
            controllers_operation_inventory.OperationInventoryController()
        )
        vital_signs = controllers_vital_signs.VitalSignalController()
        water_balance_route = (
            controllers_water_balance_route.WaterBalanceRouteController()
        )
        water_balance_annotation = (
            controllers_water_balance_annotation.WaterBalanceAnnotationController()
        )
        resident = controllers_resident.ResidentController()
        calendar_note = controllers_calendar_note.CalendarNoteController()
        nursing_note = controllers_nursing_note.NursingNoteController()
        medical_note = controllers_medical_note.MedicalNoteController()
        anomaly_level = controllers_anomaly_level.AnomalyLevelAPIController()
        anomaly = controllers_anomaly.AnomalyController()
        nutrition_level = controllers_nutrition_level.NutritionLevelAPIController()
        nutrition = controllers_nutrition.NutritionController()
        care_plan = controllers_care_plan.CarePlanController()
        mood_state = controller_mood_state.MoodStateAPIController()
        mood_answer = controller_mood_answer.MoodAnswerAPIController()
        mood_assessment = controller_mood_assessment.MoodAssessmentAPIController()
        hygiene_type = controllers_hygiene_type.HygieneTypeAPIController()
        evacuation_type = controllers_evacuation_type.EvacuationTypeAPIController()
        hygiene = controllers_hygiene.HygieneController()
        neurological_state = (
            controllers_neurological_state.NeurologicalStateAPIController()
        )
        neurological_assessment = (
            controllers_neurological_assessment.NeurologicalAssessmentController()
        )
        pain_scale = controllers_pain_scale.PainScaleController()
        norton_assessment = controllers_norton_assessment.NortonAssessmentController()
        user = controllers_user.UserController()
        scalegds5_question = (
            controllers_scalegds5_question.ScaleGDS5QuestionAPIController()
        )
        scalegds5_answer = controllers_scalegds5_answer.ScaleGDS5AnswerAPIController()
        scalegds5_assessment = (
            controllers_scalegds5_assessment.ScaleGDS5AssessmentAPIController()
        )
        scalefrail_question = (
            controllers_scalefrail_question.ScaleFRAILQuestionAPIController()
        )
        scalefrail_answer = (
            controllers_scalefrail_answer.ScaleFRAILAnswerAPIController()
        )
        scalefrail_assessment = (
            controllers_scalefrail_assessment.ScaleFRAILAssessmentAPIController()
        )
        scalesarcf_question = (
            controllers_scalesarcf_question.ScaleSARCFQuestionAPIController()
        )
        scalesarcf_answer = (
            controllers_scalesarcf_answer.ScaleSARCFAnswerAPIController()
        )
        scalesarcf_assessment = (
            controllers_scalesarcf_assessment.ScaleSARCFAssessmentAPIController()
        )
        barthel_question = controllers_barthel_question.BarthelQuestionAPIController()
        barthel_answer = controllers_barthel_answer.BarthelAnswerAPIController()
        barthel_assessment = (
            controllers_barthel_assessment.BarthelAssessmentAPIController()
        )
        lawtonbrody_question = (
            controllers_lawton_brody_question.LawtonBrodyAssessmentAPIController()
        )
        lawtonbrody_answer = (
            controllers_lawton_brody_answer.LawtonBrodyAnswerAPIController()
        )
        lawtonbrody_assessment = (
            controllers_lawton_brody_assessment.LawtonBrodyAssessmentAPIController()
        )
        medical_resident_state = controllers_medical_resident_state.MedicalResidentStateAPIController()
        laboratory_study = controllers_laboratory_study.LaboratoryStudyAPIController()

        return {
            "openapi": "3.0.0",
            "info": {
                "title": "API Serena - Care",
                "version": "1.0.0",
                "description": "API para la gestión de información con el sistema Serena - Care",
            },
            "paths": {
                "/api_serena/v1/login": {"post": auth_controller.doc_login()},
                "/api_serena/v1/logout": {"post": auth_controller.doc_logout()},
                "/api_serena/v1/list_residence_login": {
                    "get": residence.doc_get_list_residence_login()
                },
                "/api_serena/v1/list_medical_indication_this_resident": {
                    "post": medical_indication.doc_list_medical_indication_this_resident()
                },
                "/api_serena/v1/list_recreational_activity_type": {
                    "get": activity_recreational_type.doc_get_list_recreational_activity_type()
                },
                "/api_serena/v1/register_activity_recreational": {
                    "post": recreational_activity.doc_register_activity_recreational()
                },
                "/api_serena/v1/list_activity_recreational_this_resident_all": {
                    "post": recreational_activity.doc_list_activity_recreational_this_resident_all()
                },
                "/api_serena/v1/list_activity_recreational_this_resident_range": {
                    "post": recreational_activity.doc_list_activity_recreational_this_resident_range()
                },
                "/api_serena/v1/list_category_uom": {
                    "get": cat_uom.doc_get_list_category_uom()
                },
                "/api_serena/v1/list_all_uom": {"get": uom.doc_get_list_all_uom()},
                "/api_serena/v1/list_uom_this_category": {
                    "post": uom.doc_get_list_uom_this_category()
                },
                "/api_serena/v1/register_medication_intake": {
                    "post": operation_inventory.doc_register_medication_intake()
                },
                "/api_serena/v1/all_medicated_residents_this_residence_last24h": {
                    "post": operation_inventory.doc_all_medicated_residents_this_residence_last24h()
                },
                "/api_serena/v1/all_medicated_this_residents_last24h": {
                    "post": operation_inventory.doc_all_medicated_this_residents_last24h()
                },
                "/api_serena/v1/register_vital_signs": {
                    "post": vital_signs.doc_register_vital_signs()
                },
                "/api_serena/v1/list_vsigns_this_resident_all": {
                    "post": vital_signs.doc_list_vsigns_this_resident_all()
                },
                "/api_serena/v1/list_vsigns_this_resident_range": {
                    "post": vital_signs.doc_list_vsigns_this_resident_range()
                },
                "/api_serena/v1/list_water_balance_route": {
                    "get": water_balance_route.doc_get_list_water_balance_route()
                },
                "/api_serena/v1/list_wbalance_annotation_this_resident_all": {
                    "post": water_balance_annotation.doc_list_wbalance_annotation_this_resident_all()
                },
                "/api_serena/v1/list_wbalance_annotation_this_resident_range": {
                    "post": water_balance_annotation.doc_list_wbalance_annotation_this_resident_range()
                },
                "/api_serena/v1/register_water_balance_annotation": {
                    "post": water_balance_annotation.doc_register_water_balance_annotation()
                },
                "/api_serena/v1/list_residents_this_residence": {
                    "post": resident.doc_list_residents_this_residence()
                },
                "/api_serena/v1/list_familys_this_resident": {
                    "post": resident.doc_list_familys_this_resident(),
                },
                "/api_serena/v1/info_basic_this_resident": {
                    "post": resident.doc_get_info_basic_this_resident(),
                },
                "/api_serena/v1/register_calendar_note": {
                    "post": calendar_note.doc_register_calendar_note()
                },
                "/api_serena/v1/list_calendar_note_this_resident_range": {
                    "post": calendar_note.doc_list_calendar_note_this_resident_range()
                },
                "/api_serena/v1/list_calendar_note_this_resident_all": {
                    "post": calendar_note.doc_list_calendar_note_this_resident_all()
                },
                "/api_serena/v1/give_calendar_note_residence_day": {
                    "post": calendar_note.doc_give_calendar_note_residence_day()
                },
                "/api_serena/v1/register_nursing_note": {
                    "post": nursing_note.doc_register_nursing_note()
                },
                "/api_serena/v1/list_nursing_note_this_resident_range": {
                    "post": nursing_note.doc_list_nursing_note_this_resident_range()
                },
                "/api_serena/v1/list_nursing_note_this_resident_all": {
                    "post": nursing_note.doc_list_nursing_note_this_resident_all()
                },
                "/api_serena/v1/list_anomaly_level": {
                    "get": anomaly_level.doc_get_list_anomaly_level()
                },
                "/api_serena/v1/list_anomaly_this_resident_range": {
                    "post": anomaly.doc_list_anomaly_this_resident_range()
                },
                "/api_serena/v1/list_anomaly_this_resident_all": {
                    "post": anomaly.doc_list_anomaly_this_resident_all()
                },
                "/api_serena/v1/register_anomaly": {
                    "post": anomaly.doc_register_anomaly()
                },
                "/api_serena/v1/list_last_critical_or_moderate_anomalies_residents_this_residence": {
                    "post": anomaly.doc_list_latest_critical_or_moderate_anomalies_residents_this_residence()
                },
                "/api_serena/v1/list_nutrition_level": {
                    "get": nutrition_level.doc_get_list_nutrition_level()
                },
                "/api_serena/v1/list_nutrition_this_resident_range": {
                    "post": nutrition.doc_list_nutrition_this_resident_range()
                },
                "/api_serena/v1/list_nutrition_this_resident_all": {
                    "post": nutrition.doc_list_nutrition_this_resident_all()
                },
                "/api_serena/v1/register_nutrition": {
                    "post": nutrition.doc_register_nutrition()
                },
                "/api_serena/v1/care_plan_this_resident": {
                    "post": care_plan.doc_get_care_plan_this_resident()
                },
                "/api_serena/v1/list_mood_state": {
                    "get": mood_state.doc_get_list_mood_state()
                },
                "/api_serena/v1/register_mood_answers": {
                    "post": mood_answer.doc_register_mood_answers()
                },
                "/api_serena/v1/list_mood_assessment_this_resident_range": {
                    "post": mood_assessment.doc_list_mood_assessment_this_resident_range()
                },
                "/api_serena/v1/list_mood_assessment_this_resident_all": {
                    "post": mood_assessment.doc_list_mood_assessment_this_resident_all()
                },
                "/api_serena/v1/list_hygiene_type": {
                    "get": hygiene_type.doc_get_list_hygiene_type()
                },
                "/api_serena/v1/list_evacuation_type": {
                    "get": evacuation_type.doc_get_list_evacuation_type()
                },
                "/api_serena/v1/list_hygiene_this_resident_range": {
                    "post": hygiene.doc_list_hygiene_this_resident_range()
                },
                "/api_serena/v1/list_hygiene_this_resident_all": {
                    "post": hygiene.doc_list_hygiene_this_resident_all()
                },
                "/api_serena/v1/register_hygiene": {
                    "post": hygiene.doc_register_hygiene()
                },
                "/api_serena/v1/list_neurological_state": {
                    "get": neurological_state.doc_get_list_neurological_state()
                },
                "/api_serena/v1/register_neurological_assessment": {
                    "post": neurological_assessment.doc_register_neurological_assessment()
                },
                "/api_serena/v1/list_neurological_assessment_this_resident_all": {
                    "post": neurological_assessment.doc_list_neurological_assessment_this_resident_all()
                },
                "/api_serena/v1/list_neurological_assessment_this_resident_range": {
                    "post": neurological_assessment.doc_list_neurological_assessment_this_resident_range()
                },
                "/api_serena/v1/register_pain_scale": {
                    "post": pain_scale.doc_register_pain_scale()
                },
                "/api_serena/v1/list_pain_scale_this_resident_range": {
                    "post": pain_scale.doc_list_pain_scale_this_resident_range()
                },
                "/api_serena/v1/list_pain_scale_this_resident_all": {
                    "post": pain_scale.doc_list_pain_scale_this_resident_all()
                },
                "/api_serena/v1/register_norton_assessment": {
                    "post": norton_assessment.doc_register_norton_assessment()
                },
                "/api_serena/v1/list_norton_assessment_this_resident_all": {
                    "post": norton_assessment.doc_list_norton_assessment_this_resident_all()
                },
                "/api_serena/v1/list_norton_assessment_this_resident_range": {
                    "post": norton_assessment.doc_list_norton_assessment_this_resident_range()
                },
                "/api_serena/v1/list_medical_note_this_resident_range": {
                    "post": medical_note.doc_list_medical_note_this_resident_range()
                },
                "/api_serena/v1/list_medical_note_this_resident_all": {
                    "post": medical_note.doc_list_medical_note_this_resident_all()
                },
                "/api_serena/v1/profile_user": {
                    "post": user.doc_get_profile_this_user()
                },
                "/api_serena/v1/list_gds5_question": {
                    "get": scalegds5_question.doc_get_list_gds5_question()
                },
                "/api_serena/v1/register_gds5_answers": {
                    "post": scalegds5_answer.doc_register_gds5_answers()
                },
                "/api_serena/v1/list_gds5_assessment_this_resident_all": {
                    "post": scalegds5_assessment.doc_list_gds5_assessment_this_resident_all()
                },
                "/api_serena/v1/list_gds5_assessment_this_resident_range": {
                    "post": scalegds5_assessment.doc_list_gds5_assessment_this_resident_range()
                },
                "/api_serena/v1/list_frail_question": {
                    "get": scalefrail_question.doc_get_list_frail_question()
                },
                "/api_serena/v1/register_frail_answers": {
                    "post": scalefrail_answer.doc_register_frail_answers()
                },
                "/api_serena/v1/list_frail_assessment_this_resident_all": {
                    "post": scalefrail_assessment.doc_list_frail_assessment_this_resident_all()
                },
                "/api_serena/v1/list_frail_assessment_this_resident_range": {
                    "post": scalefrail_assessment.doc_list_frail_assessment_this_resident_range()
                },
                "/api_serena/v1/list_sarcf_question": {
                    "get": scalesarcf_question.doc_get_list_sarcf_question()
                },
                "/api_serena/v1/register_sarcf_answers": {
                    "post": scalesarcf_answer.doc_register_sarcf_answers()
                },
                "/api_serena/v1/list_sarcf_assessment_this_resident_all": {
                    "post": scalesarcf_assessment.doc_list_sarcf_assessment_this_resident_all()
                },
                "/api_serena/v1/list_sarcf_assessment_this_resident_range": {
                    "post": scalesarcf_assessment.doc_list_sarcf_assessment_this_resident_range()
                },
                "/api_serena/v1/list_barthel_question": {
                    "get": barthel_question.doc_get_list_barthel_question()
                },
                "/api_serena/v1/register_barthel_answers": {
                    "post": barthel_answer.doc_register_barthel_answers()
                },
                "/api_serena/v1/list_barthel_assessment_this_resident_all": {
                    "post": barthel_assessment.doc_list_barthel_assessment_this_resident_all()
                },
                "/api_serena/v1/list_barthel_assessment_this_resident_range": {
                    "post": barthel_assessment.doc_list_barthel_assessment_this_resident_range()
                },
                "/api_serena/v1/list_lawtonbrody_question": {
                    "get": lawtonbrody_question.doc_get_list_lawtonbrody_question()
                },
                "/api_serena/v1/register_lawtonbrody_answers": {
                    "post": lawtonbrody_answer.doc_register_lawtonbrody_answers()
                },
                "/api_serena/v1/list_lawtonbrody_assessment_this_resident_all": {
                    "post": lawtonbrody_assessment.doc_list_lawtonbrody_assessment_this_resident_all()
                },
                "/api_serena/v1/list_lawtonbrody_assessment_this_resident_range": {
                    "post": lawtonbrody_assessment.doc_list_lawtonbrody_assessment_this_resident_range()
                },
                "/api_serena/v1/get_general_condition_residents_of_residence": {
                    "post": medical_resident_state.doc_get_general_condition_residents_of_residence()
                },
                "/api_serena/v1/list_laboratory_study_this_resident":{
                   "post": laboratory_study.doc_list_laboratory_study_this_resident() 
                }
                # Agregar más endpoints aquí según sea necesario
            },
            "components": {
                "securitySchemes": {
                    "bearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT",
                    }
                }
            },
        }

    def _render_swagger_ui(self, openapi_spec):
        """Renderiza la interfaz HTML con Swagger UI"""
        html_content = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <title>API Serena - Documentación</title>
            <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@3.52.5/swagger-ui.css" />
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                    background-color: #fafafa;
                }}
                .swagger-ui .info hgroup.main h2 {{
                    color: #3b4151;
                    font-size: 24px;
                }}
                .topbar {{
                    background-color: #2c3e50;
                    padding: 10px 20px;
                    color: white;
                    font-size: 18px;
                    font-weight: bold;
                }}
            </style>
        </head>
        <body>
            <div class="topbar">API Serena - Documentación</div>
            <div id="swagger-ui"></div>
            
            <script src="https://unpkg.com/swagger-ui-dist@3.52.5/swagger-ui-bundle.js"></script>
            <script src="https://unpkg.com/swagger-ui-dist@3.52.5/swagger-ui-standalone-preset.js"></script>
            <script>
                const spec = {json.dumps(openapi_spec)};
                
                // Configuración de Swagger UI
                const ui = SwaggerUIBundle({{
                    spec: spec,
                    dom_id: '#swagger-ui',
                    presets: [
                        SwaggerUIBundle.presets.apis,
                        SwaggerUIBundle.StandalonePreset
                    ],
                    layout: "BaseLayout",
                    deepLinking: true,
                    showExtensions: true,
                    showCommonExtensions: true,
                    docExpansion: 'none',
                    filter: true,
                    tagsSorter: 'alpha',
                    operationsSorter: 'alpha'
                }});
                
                // Agregar interceptor para manejar autenticación si es necesario
                ui.initOAuth({{
                    clientId: 'your-client-id',
                    clientSecret: 'your-client-secret',
                    realm: 'your-realms',
                    appName: 'API Serena',
                    scopeSeparator: ' ',
                    additionalQueryStringParams: {{}}
                }});
            </script>
        </body>
        </html>
        """

        return Response(html_content, headers={"Content-Type": "text/html"})

    def extract_docs(self, method):
        """
        Extrae la documentación OpenAPI del docstring de un método

        Args:
            method: El método del controlador con documentación OpenAPI en su docstring

        Returns:
            dict: Diccionario con la documentación OpenAPI parseada
        """
        if not method or not method.__doc__:
            _logger.warning(f"Método o docstring no encontrado para: {method}")
            return {}

        docstring = method.__doc__

        # Buscar el contenido YAML dentro del docstring
        yaml_content = self._extract_yaml_from_docstring(docstring)

        if not yaml_content:
            _logger.warning(
                f"No se encontró contenido YAML en el docstring de: {method.__name__}"
            )
            return {}

        try:
            # Parsear el YAML a un diccionario de Python
            parsed_docs = yaml.safe_load(yaml_content)
            return parsed_docs
        except yaml.YAMLError as e:
            _logger.error(f"Error al parsear YAML del método {method.__name__}: {e}")
            return {}

    def _extract_yaml_from_docstring(self, docstring):
        """
        Extrae el contenido YAML de un docstring que contiene documentación OpenAPI

        Args:
            docstring (str): El docstring completo del método

        Returns:
            str: El contenido YAML extraído, o None si no se encuentra
        """
        # Patrón para encontrar el bloque YAML (entre --- y el final o otro ---)
        pattern = r"^-{3}\s*\n(.*?)(?=^-{3}|\Z)"
        match = re.search(pattern, docstring, re.DOTALL | re.MULTILINE)

        if match:
            return match.group(1).strip()

        # Si no encuentra el patrón ---, buscar cualquier contenido YAML-like
        lines = docstring.split("\n")
        yaml_lines = []
        in_yaml_block = False

        for line in lines:
            # Buscar líneas que parezcan YAML (con indentación y :)
            if re.match(r"^\s*[a-zA-Z]+:", line) or in_yaml_block:
                in_yaml_block = True
                yaml_lines.append(line)
            # Detener si encontramos una línea que no es YAML y estábamos en un bloque
            elif in_yaml_block and line.strip() and not re.match(r"^\s", line):
                break

        if yaml_lines:
            return "\n".join(yaml_lines)

        return None
