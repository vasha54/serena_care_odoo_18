from odoo import http
from odoo.http import request
import base64
import logging

_logger = logging.getLogger(__name__)

class PublicImageController(http.Controller):

    @http.route(['/public/image/mood_state/<int:mood_state_id>'],
                type='http', auth='public', website=True, methods=['GET'], csrf=False)
    def serve_public_mood_state_image(self, mood_state_id, **kwargs):
        """
        Public controller to serve res.partner images without authentication
        Access via: /public/image/partner/123
        """
        try:
            # Find the partner record using superuser privileges
            mood_state = request.env['mood.state'].sudo().browse(mood_state_id)

            if not mood_state.exists() or not mood_state.image:
                # Return default image or 404 if no partner or image found
                return request.not_found()

            # Extract image data and format
            image_data = base64.b64decode(mood_state.image)
            image_content_type = self._get_image_content_type(mood_state.image)

            # Serve the image with caching headers
            return request.make_response(
                image_data,
                headers=[
                    ('Content-Type', image_content_type),
                    ('Cache-Control', 'public, max-age=86400'),  # Cache for 24 hours
                ]
            )

        except Exception as e:
            # Log error and return 404
            _logger.error("Error serving public partner image: %s", str(e))
            return request.not_found()

    @http.route(['/public/image/user/<int:user_id>'],
                type='http', auth='public', website=True, methods=['GET'], csrf=False)
    def serve_public_user_image(self, user_id, **kwargs):
        """
        Public controller to serve res.partner images without authentication
        Access via: /public/image/partner/123
        """
        try:
            # Find the partner record using superuser privileges
            partner = request.env['res.users'].sudo().browse(user_id)

            if not partner.exists() or not partner.image_1920:
                # Return default image or 404 if no partner or image found
                return request.not_found()

            # Extract image data and format
            image_data = base64.b64decode(partner.image_1920)
            image_content_type = self._get_image_content_type(partner.image_1920)

            # Serve the image with caching headers
            return request.make_response(
                image_data,
                headers=[
                    ('Content-Type', image_content_type),
                    ('Cache-Control', 'public, max-age=86400'),  # Cache for 24 hours
                ]
            )

        except Exception as e:
            # Log error and return 404
            _logger.error("Error serving public partner image: %s", str(e))
            return request.not_found()


    @http.route(['/public/image/recreational_activity_type/<int:ra_type>'],
                type='http', auth='public', website=True, methods=['GET'], csrf=False)
    def serve_public_recreational_activity_type_image(self, ra_type, **kwargs):
        """
        Public controller to serve nomenclature.activity.type images without authentication
        Access via: /public/image/recreational_activity_type/123
        """
        try:
            # Find the partner record using superuser privileges
            activity_type = request.env['nomenclature.activity.type'].sudo().browse(ra_type)

            if not activity_type.exists() or not activity_type.image:
                # Return default image or 404 if no partner or image found
                return request.not_found()

            # Extract image data and format
            image_data = base64.b64decode(activity_type.image)
            image_content_type = self._get_image_content_type(activity_type.image)

            # Serve the image with caching headers
            return request.make_response(
                image_data,
                headers=[
                    ('Content-Type', image_content_type),
                    ('Cache-Control', 'public, max-age=86400'),  # Cache for 24 hours
                ]
            )

        except Exception as e:
            # Log error and return 404
            _logger.error("Error serving public partner image: %s", str(e))
            return request.not_found()

    @http.route(['/public/image/resident/<int:resident_id>'], 
                type='http', auth='public', website=True, methods=['GET'], csrf=False)
    def serve_public_resident_image(self, resident_id, **kwargs):
        """
        Public controller to serve res.partner images without authentication
        Access via: /public/image/partner/123
        """
        try:
            # Find the partner record using superuser privileges
            partner = request.env['resident'].sudo().browse(resident_id)
            
            if not partner.exists() or not partner.image_1920:
                # Return default image or 404 if no partner or image found
                return request.not_found()
            
            # Extract image data and format
            image_data = base64.b64decode(partner.image_1920)
            image_content_type = self._get_image_content_type(partner.image_1920)
            
            # Serve the image with caching headers
            return request.make_response(
                image_data,
                headers=[
                    ('Content-Type', image_content_type),
                    ('Cache-Control', 'public, max-age=86400'),  # Cache for 24 hours
                ]
            )
            
        except Exception as e:
            # Log error and return 404
            _logger.error("Error serving public partner image: %s", str(e))
            return request.not_found()

    @http.route(['/public/image/family_resident/<int:family_id>'], 
                type='http', auth='public', website=True, methods=['GET'], csrf=False)
    def serve_public_family_resident_image(self, family_id, **kwargs):
        """
        Public controller to serve res.partner images without authentication
        Access via: /public/image/partner/123
        """
        try:
            # Find the partner record using superuser privileges
            partner = request.env['resident.family'].sudo().browse(family_id)
            
            if not partner.exists() or not partner.image_1920:
                # Return default image or 404 if no partner or image found
                return request.not_found()
            
            # Extract image data and format
            image_data = base64.b64decode(partner.image_1920)
            image_content_type = self._get_image_content_type(partner.image_1920)
            
            # Serve the image with caching headers
            return request.make_response(
                image_data,
                headers=[
                    ('Content-Type', image_content_type),
                    ('Cache-Control', 'public, max-age=86400'),  # Cache for 24 hours
                ]
            )
            
        except Exception as e:
            # Log error and return 404
            _logger.error("Error serving public partner image: %s", str(e))
            return request.not_found()
    
    def _get_image_content_type(self, image_data):
        """
        Detect image content type from base64 data
        Simple detection - in production you might want more robust detection
        """
        if image_data.startswith(b'/9j/'):
            return 'image/jpeg'
        elif image_data.startswith(b'iVBORw0KGgo'):
            return 'image/png'
        elif image_data.startswith(b'R0lGODdh'):
            return 'image/gif'
        else:
            return 'image/jpeg'  # Default fallback
