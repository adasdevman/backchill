import cloudinary
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class CloudinaryConfigView(APIView):
    """
    Vue pour récupérer les informations de configuration Cloudinary
    pour l'application mobile.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            # Récupérer les informations de configuration Cloudinary
            cloud_name = settings.CLOUDINARY_STORAGE.get('CLOUD_NAME', '')
            api_key = settings.CLOUDINARY_STORAGE.get('API_KEY', '')
            
            # Construire la réponse
            response_data = {
                'cloudinary': {
                    'cloud_name': cloud_name,
                    'api_key': api_key,
                    'upload_preset': 'ml_default',  # Preset que vous avez mentionné
                    'folder': 'mobile_uploads',
                    'resource_types': ['image', 'video'],
                    'video_transformations': 'q_auto:eco,vc_auto'  # Optimisations par défaut
                }
            }
            
            return Response(response_data)
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la configuration Cloudinary: {str(e)}", exc_info=True)
            return Response({
                'error': f'Impossible de récupérer la configuration Cloudinary: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
